from django.shortcuts import render
from .models import Slogan
from .models import Anakategori
from .models import Urun
from django.db.models import Q

# Create your views here.

def index(request):
    slogan = Slogan.objects.first()
    anakategori = Anakategori.objects.all()
    urunler = Urun.objects.all()
    context = {
        'slogan': slogan,
        'anakategori' : anakategori,
        'urunler' : urunler,
    }
    return render(request, 'index.html', context)

def register(request):
    anakategori = Anakategori.objects.all()
    context = {
        'anakategori' : anakategori,
    }
    return render(request, 'register.html', context)

def login(request):
    anakategori = Anakategori.objects.all()
    context = {
        'anakategori' : anakategori,
    }
    return render(request, 'login.html', context)

# def allProduct(request):
#     urunler = Urun.objects.all()
#     anakategori = Anakategori.objects.all()
#     context = {
#         'anakategori' : anakategori,
#         'urunler' : urunler,
#     }

#     return render(request, 'all-product.html', context)



def allProduct(request):
    urunler = Urun.objects.all()
    anakategori = Anakategori.objects.all()
    sort_option = request.GET.get('sort_option')
    search_query = request.GET.get('search_query')

    if search_query:
        urunler = urunler.filter(
            Q(isim__icontains=search_query) |
            Q(kategori__icontains=search_query) |
            Q(urunRengi__icontains=search_query) |
            Q(aciklama__icontains=search_query)
        )

    if sort_option == 'asc':
        urunler = urunler.order_by('fiyat')
    elif sort_option == 'desc':
        urunler = urunler.order_by('-fiyat')

    context = {
        'anakategori': anakategori,
        'urunler': urunler,
        'sort_option': sort_option,
        'search_query': search_query,
    }

    if search_query and not urunler.exists():
        context['no_results'] = True

    return render(request, 'all-product.html', context)


def category(request,categoryName):
    urunler = Urun.objects.filter(kategori=categoryName)
    anakategori = Anakategori.objects.all()
    context = {
        'anakategori' : anakategori,
        'urunler' : urunler,
        'kategori': categoryName,
    }
    return render(request, 'category.html',context)

def productDetail(request, urunId):
    urunum = Urun.objects.get(id = urunId)
    anakategori = Anakategori.objects.all()
    context = {
        'anakategori' : anakategori,
        'urun' : urunum
    }
    return render(request, 'product-detail.html', context)


def aboutUs(request):
    anakategori = Anakategori.objects.all()
    context = {
        'anakategori' : anakategori,
    }
    return render(request, 'about-us.html', context)

def contactUs(request):
    anakategori = Anakategori.objects.all()
    context = {
        'anakategori' : anakategori,
    }
    return render(request, 'contact-us.html', context)



