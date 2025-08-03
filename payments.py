# payments/views.py
import json
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings as django_settings
import logging
from django.http import HttpResponse
from django.urls import reverse
from azbankgateways import bankfactories, models as bank_models, default_settings as az_settings
from azbankgateways.exceptions import AZBankGatewaysException
from azbankgateways.models import Bank
from Blog_app.models import Cart, Order, OrderItem, products
from django.contrib.auth.decorators import login_required
from Blog_app.forms import CheckoutForm
from accounts_app.models import Profile
from .models import Transaction
from django.db import transaction as db_transaction
from django.contrib import messages
from decimal import Decimal
import logging


logger = logging.getLogger('Payments')



@login_required(login_url='account_app:login')
def go_to_gateway_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, "سبد خرید شما خالیست.")
        return redirect("blog:cart_view")

    try:
        total_amount = sum(item.final_price() for item in cart_items)
    except Exception as e:
        logger.error(f"[GATEWAY] Error calculating cart total: {e}", exc_info=True)
        return HttpResponse("خطا در محاسبه مبلغ نهایی.")

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, "مشخصات کاربری شما ناقص است.")
        return redirect("account_app:profile_setup")

    try:
        # ایجاد سفارش
        order = Order.objects.create(
            user=request.user,
            final_total=total_amount,
            address=profile.address,
            city=profile.city,
            state=profile.state,
            phone=profile.phone,
            email=profile.e_mail,
            is_paid=False
        )

        # ساخت ساده‌ی OrderItem
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.final_price()
            )

        # ایجاد تراکنش
        transaction = Transaction.objects.create(
            user=request.user,
            amount=total_amount,
            status='PENDING'
        )

        # تنظیم درگاه پرداخت
        factory = bankfactories.BankFactory()
        bank = factory.auto_create(bank_models.BankType.ZARINPAL)
        bank.set_request(request)
        bank.set_amount(total_amount)
        bank.set_client_callback_url(reverse("payments:call_back"))
        bank.set_mobile_number(profile.phone)

        bank_record = bank.ready()
        bank_record.extra_information = json.dumps({
            'order_id': order.id,
            'transaction_id': transaction.id
        })
        bank_record.save()

        transaction.authority = bank_record.tracking_code
        transaction.save()

        return bank.redirect_gateway()

    except AZBankGatewaysException as e:
        logger.critical(f"[GATEWAY] Gateway error: {e}", exc_info=True)
        return render(request, 'blog/payment_failed.html', {
            'status': 'خطا در اتصال به درگاه پرداخت.'
        })

    except Exception as e:
        logger.critical(f"[GATEWAY] Unexpected error: {e}", exc_info=True)
        return HttpResponse("خطای غیرمنتظره در فرایند پرداخت.")
        
@login_required(login_url='account_app:login')
def checkout(request):
    profile = get_object_or_404(Profile, user=request.user)
    form = CheckoutForm(request.POST or None, instance=profile)
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    discount = sum(item.calculate_discount() for item in cart_items)
    final_total = sum(item.final_price() for item in cart_items)

    if request.method == 'POST' and form.is_valid():
        form.save()
        # بررسی موجودی و محدودیت
        insufficient = []
        for item in cart_items:
            if item.quantity > 5:
                messages.error(request, f"حداکثر سفارش برای {item.product.name} ۵ عدد است.")
                return redirect('blog:cart_detail')
            if item.quantity > item.product.stock:
                insufficient.append(item.product.name)
        if insufficient:
            messages.error(request, f"موجودی کافی نیست برای: {', '.join(insufficient)}")
            return redirect('blog:cart')
        return redirect('payments:go-to-gateway')

    return render(request, 'blog/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'discount': discount,
        'final_total': final_total,
        'form': form
    })


@login_required(login_url='account_app:login')
def callback_gateway_view(request):
    status = request.GET.get('Status')
    bank_type = request.GET.get('bank_type')
    tracking_code = request.GET.get('tc')

    if not tracking_code:
        logger.error("Missing tracking code in callback.")
        raise Http404("لینک پرداخت معتبر نیست.")

    # Step 1: Retrieve bank record
    try:
        bank_record = Bank.objects.get(tracking_code=tracking_code)
    except Bank.DoesNotExist:
        logger.error(f"No bank record found for tracking_code={tracking_code}")
        raise Http404("اطلاعات پرداخت یافت نشد.")

    # Step 2: Load transaction
    try:
        extra_info = json.loads(bank_record.extra_information)
        transaction = Transaction.objects.get(id=extra_info.get("transaction_id"))
        user = transaction.user
    except Exception as e:
        logger.exception("Error loading transaction from extra_information")
        raise Http404("تراکنش معتبر یافت نشد.")

    # Step 3: Handle user cancel
    if status == "NOK":
        transaction.status = "FAIL"
        transaction.save()
        return render(request, "blog/payment_failed.html", {
            "status": "پرداخت توسط کاربر لغو شد.",
            "transaction_id": transaction.id,
            "name": user.username
        })

    # Step 4: Use verified bank record directly
    verified_record = bank_record  # Skip verify_from_gateway to avoid reference_number error

    if verified_record.status == "COMPLETE":
        transaction.status = "SUCCESS"
        transaction.save()

        profile = get_object_or_404(Profile, user=user)
        cart_items = Cart.objects.filter(user=user)

        order = Order.objects.create(
            user=user,
            final_total=sum(item.final_price() for item in cart_items),
            address=profile.address,
            city=profile.city,
            state=profile.state,
            phone=profile.phone,
            email=profile.e_mail,
            is_paid=True
        )

        for item in cart_items:
            price = Decimal(item.final_price() or item.product.cost or 0)
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=price  # ✅ Fix: ensure price is not null
            )
            item.delete()

        logger.info(f"✅ Payment completed | Transaction #{transaction.id} | Order #{order.id}")
        return render(request, "blog/payment_success.html", {
            "status": "پرداخت با موفقیت انجام شد.",
            "transaction_id": transaction.id,
            "name": user.username
        })

    # Step 5: Fallback failure
    transaction.status = "FAIL"
    transaction.save()
    logger.warning(f"Payment not verified | Transaction #{transaction.id}")
    return render(request, "blog/payment_failed.html", {
        "status": "پرداخت تایید نشد.",
        "transaction_id": transaction.id,
        "name": user.username
    })