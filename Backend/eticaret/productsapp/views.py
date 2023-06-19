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

def login(request):
    return render(request, 'login-register.html')

def category(request):
    return render(request, 'category.html')

def productDetail(request):
    return render(request, 'product-detail.html')

def aboutUs(request):
    return render(request, 'about-us.html')

def contactUs(request):
    return render(request, 'contact-us.html')


