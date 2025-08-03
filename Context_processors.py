from Blog_app.models import products, Category,Cart
from home_app.models import logo_definer
from django.core.paginator import Paginator
from django.shortcuts import render


def recent_articles(request):
    recent_articles = products.objects.order_by("-created")[:3]

    return {"recent_articles": recent_articles}


def categories(request):
    categories = Category.objects.all()

    return {'categories': categories}


def logo(request):
    logos = logo_definer.objects.order_by('-add_logo')
    logo = logos[0] if logos.exists() else None
    return {'logo': logo}





def cart_items_processor(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total = sum(item.total_price() for item in cart_items)
        discount = sum(item.calculate_discount() for item in cart_items)
        final_total = sum(item.final_price() for item in cart_items)
        item_count = sum(item.quantity for item in cart_items)  # Calculate total item count
        return {
            'cart_items': cart_items,
            'total': total,
            'discount': discount,
            'final_total': final_total,
            'item_count': item_count  # Add item count to context
        }
    return {}




def search(request):
    q = request.GET.get('q')
    context = {'query': q}
    if q:
        product_list = products.objects.filter(name__icontains=q)
        paginator = Paginator(product_list, 10)
        page_number = request.GET.get('page')
        objectlist = paginator.get_page(page_number)
        context['products_by_category'] = objectlist
    else:
        context['products_by_category'] = []
    return context

