from django.contrib import messages
from django.shortcuts import redirect,render
from django.contrib.auth import authenticate, login, logout
import re
import phonenumbers
from .models import MyUser
from productsapp.models import Anakategori
from productsapp.models import SocialMedia
from productsapp.models import Footer
from productsapp.models import *
from .forms import UserProfileForm
from decimal import Decimal

def is_valid_phone_number(phone_number, country_code):
    try:
        parsed_number = phonenumbers.parse(phone_number, country_code)
        return phonenumbers.is_valid_number(parsed_number)
    except phonenumbers.phonenumberutil.NumberParseException:
        return False

def login_request(request):
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    anakategori = Anakategori.objects.all()
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST["password"]
        remember_me = request.POST.get('remember_me') 

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if remember_me:
                request.session.set_expiry(3600)
            return redirect('index')
        else:
            return render(request, "login.html", {
                'error': 'Kullanıcı adı veya parola hatalı',
                'anakategori': anakategori,
                'footer': footer,
                'social_media': socail_media,
            })
    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
    }
    return render(request, 'login.html', context)

def register(request):
    anakategori = Anakategori.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        phone = request.POST["phone"]
        password = request.POST['password']
        repassword = request.POST['repassword']
        accept_terms = request.POST.get('accept_terms')
        accept_privacy = request.POST.get('accept_privacy')

        if not username.strip() or not email or not accept_terms or not accept_privacy:
            return render(request, 'register.html',
                        {
                            'error': 'Kullanıcı adı, e-posta, üyelik sözleşmesi ve kişisel veri aydınlatma metni kabul edilmelidir.',
                            'username': username,
                            'email': email,
                            'firstname': firstname,
                            'lastname': lastname,
                            'phone': phone,
                            'anakategori': anakategori,
                            'footer': footer,
                            'social_media': socail_media,
                        })

        if ' ' in username or re.search(r'[ğüşıöçĞÜŞİÖÇ]', username):
            return render(request, 'register.html',
                        {
                            'error': 'Kullanıcı adı boşluk içeremez ve Türkçe karakterler içeremez.',
                            'username': username,
                            'email': email,
                            'firstname': firstname,
                            'lastname': lastname,
                            'phone': phone,
                            'anakategori': anakategori,
                            'footer': footer,
                            'social_media': socail_media,
                        })

        if password == repassword:
            if MyUser.objects.filter(username=username).exists():
                return render(request, 'register.html',
                            {
                                'error': 'Bu kullanıcı adı daha önce alınmış',
                                'username': username,
                                'email': email,
                                'firstname': firstname,
                                'lastname': lastname,
                                'phone': phone,
                                'anakategori': anakategori,
                                'footer': footer,
                                'social_media': socail_media,
                            })
            else:
                if MyUser.objects.filter(email=email).exists():
                    return render(request, 'register.html',
                                {
                                    'error': 'Bu email daha önce alınmış',
                                    'username': username,
                                    'email': email,
                                    'firstname': firstname,
                                    'lastname': lastname,
                                    'phone': phone,
                                    'anakategori': anakategori,
                                    'footer': footer,
                                    'social_media': socail_media,
                                })
                else:
                    if not re.search(r'^(?=.*[a-z])(?=.*[A-Z]).{8,}$', password):
                        return render(request, 'register.html',
                                    {
                                        'error': 'Parola en az 8 karakter uzunluğunda olmalı ve en az bir büyük harf ve bir küçük harf içermelidir.',
                                        'username': username,
                                        'email': email,
                                        'firstname': firstname,
                                        'lastname': lastname,
                                        'phone': phone,
                                        'anakategori': anakategori,
                                        'footer': footer,
                                        'social_media': socail_media,
                                    })

                    if not is_valid_phone_number(phone, 'TR'):  # Telefon numarasını geçerlilik kontrolü yapmak için ülke kodunu uygun şekilde ayarlayın
                        return render(request, 'register.html',
                                    {
                                        'error': 'Geçersiz telefon numarası',
                                        'username': username,
                                        'email': email,
                                        'firstname': firstname,
                                        'lastname': lastname,
                                        'phone': phone,
                                        'anakategori': anakategori,
                                        'footer': footer,
                                        'social_media': socail_media,
                                    })
                    user = MyUser.objects.create_user(username=username, email=email, first_name=firstname,last_name=lastname, password=password, phone=phone)
                    user.save()
                    return redirect('login')
        else:
            return render(request, 'register.html',
                        {
                            'error': 'Parolalar eşleşmiyor',
                            'username': username,
                            'email': email,
                            'firstname': firstname,
                            'lastname': lastname,
                            'phone': phone,
                            'anakategori': anakategori,
                            'footer': footer,
                            'social_media': socail_media,
                        })

    context = {
        'anakategori': anakategori,
        'footer': footer,
        'social_media': socail_media,
    }
    return render(request, 'register.html', context)

def logout_request(request):
    logout(request)
    return redirect('index')


def teslimat(request):
    anakategori = Anakategori.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
    }
    return render(request, 'teslimat-bilgileri.html', context)

def update_profile(request):

    anakategori = Anakategori.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()

    # Navbardaki Sepet Kısmında adet ve fiyat göstermek için
    user = request.user
    toplam_tutar = Decimal('0.00')
    toplam_urun_sayisi = 0

    if user.is_authenticated:  # Kullanıcı girişi yapılmışsa
        sepetim = Sepet.objects.filter(user=user)
        for sepet in sepetim:
            toplam_tutar += sepet.hesapla_toplam()
            toplam_urun_sayisi += sepet.adet
    else:  # Kullanıcı girişi yapılmamışsa, boş bir sepet listesi oluştur
        sepetim = []

    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            new_username = form.cleaned_data['username']
            new_email = form.cleaned_data['email']

            # Kullanıcı adı veya e-posta zaten alınmış mı kontrol et
            if MyUser.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                messages.error(request, 'Bu kullanıcı adı zaten kullanılıyor.')
            elif MyUser.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                messages.error(request, 'Bu e-posta adresi zaten kullanılıyor.')
            else:
                user.username = new_username
                user.email = new_email
                user.first_name = form.cleaned_data['firstname']
                user.last_name = form.cleaned_data['lastname']
                user.phone = form.cleaned_data['phone']
                user.address = form.cleaned_data['address']
                user.save()
                messages.success(request, 'Profiliniz güncellendi.')
                return redirect('update_profile')
    else:
        form = UserProfileForm(initial={
            'username': request.user.username,
            'email': request.user.email,
            'firstname': request.user.first_name,
            'lastname': request.user.last_name,
            'phone': request.user.phone,
            'address': request.user.address
        })

    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
        'form':form,

        # Navbardaki Sepet Kısmında adet ve fiyat göstermek için
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi

    }
    return render(request, 'hesabim.html', context)