from django.shortcuts import render
from .models import Slogan

# Create your views here.

def index(request):
    slogan = Slogan.objects.first()
    context = {
        'slogan': slogan,
    }
    return render(request, 'index.html', context)

def login(request):
    return render(request, 'login-register.html')
