from django.contrib import messages
from django.shortcuts import redirect,render
from django.contrib.auth import authenticate, login, logout
import re
import phonenumbers
from .models import MyUser
from productsapp.models import Anakategori
from productsapp.models import SocialMedia
from productsapp.models import Footer

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
                'error': 'Kullanıcı adı veya parola hatalı'
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

        if not username or not email or not accept_terms or not accept_privacy:
            return render(request, 'register.html', 
            {
                'error': 'Kullanıcı adı, e-posta, üyelik sözleşmesi ve kişisel veri aydınlatma metni kabul edilmelidir.',
                'username': username,
                'email': email,
                'firstname': firstname,
                'lastname': lastname,
                'phone': phone,
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
                        })

                    user = MyUser.objects.create_user(username=username, email=email, first_name=firstname, last_name=lastname, password=password, phone=phone)
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
            })
    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
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