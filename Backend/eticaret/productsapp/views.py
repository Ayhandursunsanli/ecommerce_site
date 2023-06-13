from django.shortcuts import render
from .models import Slogan
from .models import Anakategori

# Create your views here.

def index(request):
    slogan = Slogan.objects.first()
    anakategori = Anakategori.objects.all()
    context = {
        'slogan': slogan,
        'anakategori' : anakategori,
    }
    return render(request, 'index.html', context)

def login(request):
    return render(request, 'login-register.html')
