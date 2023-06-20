from django.shortcuts import render
from .models import Slogan
from .models import Anakategori
from .models import Urun

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
    return render(request, 'register.html')

def login(request):
    return render(request, 'login.html')

def category(request):
    urunler = Urun.objects.all()
    context = {
        'urunler' : urunler,
    }

    return render(request, 'category.html', context)

def productDetail(request, urunId):
    urunum = Urun.objects.get(id = urunId)
    context = {
        'urun' : urunum
    }
    return render(request, 'product-detail.html', context)
    

def aboutUs(request):
    return render(request, 'about-us.html')

def contactUs(request):
    return render(request, 'contact-us.html')


