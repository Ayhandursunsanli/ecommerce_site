
from productsapp.models import Anakategori
from productsapp.models import SocialMedia
from productsapp.models import Footer
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import re

def userRegister(request):
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    anakategori = Anakategori.objects.all()

    if request.method == 'POST':
        kullanici = request.POST['kullanici']
        email = request.POST['email']
        sifre1 = request.POST['sifre1']
        sifre2 = request.POST['sifre2']
        accept_terms = request.POST.get('accept_terms')
        accept_privacy = request.POST.get('accept_privacy')
        # isim = request.POST['isim']
        # soyisim = request.POST['soyisim']
        
        if kullanici != '' and email != '' and sifre1 != '' and sifre2 != '':

            if re.search('[ğüşıöçĞÜŞİÖÇ]', kullanici):
                messages.error(request, 'Kullanıcı adında Türkçe karakter kullanılamaz!')
                return redirect('register')
            if ' ' in kullanici:
                messages.error(request, 'Kullanıcı adında boşluk kullanılamaz!')
                return redirect('register')
            if sifre1 == sifre2:
                if User.objects.filter(username = kullanici).exists():
                    messages.error(request, "Kullanıcı adı mevcut !")
                    return redirect('register')
                elif User.objects.filter(email = email).exists():
                    messages.error(request, 'Email kullanımda !')
                    return redirect('register')
                elif len(sifre1) < 8:
                    messages.error(request, 'Şifre en az 8 karakter olmalıdır !')
                    return redirect('register')
                elif not accept_terms or not accept_privacy:
                    messages.error(request, 'Üyelik sözleşmesini ve KVKK metnini kabul etmelisiniz!')
                    return redirect('register')
                else:
                    user = User.objects.create_user(
                        username = kullanici,
                        email = email,
                        password = sifre1
                    )
                    user.save()
                    messages.success(request, 'Kullanıcı oluşturuldu.')
                    return redirect('login')
            else:
                messages.error(request, 'Şifreler uyuşmuyor !')
                return redirect('register')
        else:
            messages.error(request, 'Tüm alanların doldurulması zorunludur!')
            return redirect('register')

    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
    }

    return render(request, 'register.html', context)

def userLogin(request):
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    anakategori = Anakategori.objects.all()

    if request.method == 'POST':
        kullanici = request.POST['kullanici']
        sifre = request.POST['sifre']

        user = authenticate(request, username = kullanici, password = sifre)

        if user is not None:
            login(request, user)
            messages.success(request, 'Giriş Yapıldı')
            return redirect('index')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı !')
            return redirect('login')
        
    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
    }

    return render(request, 'login.html', context)

def userLogout(request):
    logout(request)
    messages.success(request, 'Çıkış Yapıldı')
    return redirect('index')