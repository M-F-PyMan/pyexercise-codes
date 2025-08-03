from django.shortcuts import render
from Blog_app.models import products, headtitle
from .models import logo_definer, Advertisement,Special_offer


def home(request):
    product = products.objects.all()
    head = headtitle.objects.all()
    recent_products = products.objects.all()[:8]
    recent_head = headtitle.objects.all()[:8]
    adv = Advertisement.objects.all()
    adv1 = Advertisement.objects.all()[0:]
    SPO= Special_offer.objects.all()



    if adv1.exists() and adv.exists():
        return render(request, "home_app/index.html", {
            'headtitle': head,
            'products': product,
            "recent_P": recent_products,
            "recent_H": recent_head,
            'adv1': adv1,
            'adv': adv,
            'SPO':SPO
        })
    elif adv.exists() and adv1.exists() !=True:
        return render(request, "home_app/index.html", {
            'headtitle': head,
            'products': product,
            "recent_P": recent_products,
            "recent_H": recent_head,
            'adv': adv,
            'SPO': SPO
        })
    elif adv1.exists() and adv.exists() != True:
        return render(request, "home_app/index.html", {
            'headtitle': head,
            'products': product,
            "recent_P": recent_products,
            "recent_H": recent_head,
            'adv1': adv1,
            'SPO': SPO
        })
    else:
        return render(request, "home_app/index.html", {
            'headtitle': head,
            'products': product,
            "recent_P": recent_products,
            "recent_H": recent_head,
            'SPO': SPO

        })

def header_logo(request):
    image = logo_definer.objects.order_by('-add_logo')[0]

    return render(request, 'includes/header.html', context={'logo': image})
# Create your views here.
