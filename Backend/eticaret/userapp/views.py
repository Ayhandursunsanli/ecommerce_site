from django.contrib import messages
from django.shortcuts import redirect,render
from django.contrib.auth import authenticate, login, logout
import re
import phonenumbers
from .models import MyUser
from productsapp.models import *
from .forms import UserProfileForm
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

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

        # if user is not None:
        #     login(request, user)
        #     if remember_me:
        #         request.session.set_expiry(3600)
        #     return redirect('index')
        # else:
        #     return render(request, "login.html", {
        #         'error': 'Kullanıcı adı veya parola hatalı',
        #         'anakategori': anakategori,
        #         'footer': footer,
        #         'social_media': socail_media,
        #     })

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Hesabınız aktif değil. Lütfen e-posta onayınızı tamamlayın.')
                return redirect('login')
        else:
            user = MyUser.objects.filter(username=username).first()
            if user is not None and not user.is_active:
                messages.error(request, 'Hesabınız aktif değil. Lütfen e-posta onayınızı tamamlayın.')
            else:
                messages.error(request, 'Kullanıcı adı veya parola hatalı')
            return redirect('login')
    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
    }
    return render(request, 'login.html', context)

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Hesabınız başarıyla etkinleştirildi!')
        return redirect('login')
    else:
        messages.error(request, 'Aktivasyon bağlantısı geçersiz!')
        return render(request, 'login.html')

def activateEmail(request, user, to_email):
    mail_subject = 'Activate your account.'
    message = render_to_string('activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protokol': 'https://' if request.is_secure() else 'http://'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])

    # Kullanıcı adını ekle
    email.from_email = f"{user.username} <from@example.com>"

    if email.send():
        messages.success(request, f"Sayın {user.username}, lütfen e-postanızdaki {to_email} gelen kutusuna gidin ve kaydı onaylamak için alınan aktivasyon bağlantısına tıklayın.")
        return redirect('login')  # Login sayfasına yönlendirme
    else:
        messages.error(request, f"Sayın {user.username}, e-postaya aktivasyon bağlantısı gönderilirken bir hata oluştu.")
        return redirect('login')  # Login sayfasına yönlendirme

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
                    
                    if MyUser.objects.filter(phone=phone).exists():
                        return render(request, 'register.html', {
                            'error': 'Bu telefon numarası daha önce alınmış',
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
                    user.is_active = False
                    user.save()
                    activateEmail(request, user, email)
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

    city_options = [
        {"value": "1", "label": "Adana"},
        {"value": "2", "label": "Adıyaman"},
        {"value": "3", "label": "Afyonkarahisar"},
        {"value": "4", "label": "Ağrı"},
        {"value": "5", "label": "Amasya"},
        {"value": "6", "label": "Ankara"},
        {"value": "7", "label": "Antalya"},
        {"value": "8", "label": "Artvin"},
        {"value": "9", "label": "Aydın"},
        {"value": "10", "label": "Balıkesir"},
        {"value": "11", "label": "Bilecik"},
        {"value": "12", "label": "Bingöl"},
        {"value": "13", "label": "Bitlis"},
        {"value": "14", "label": "Bolu"},
        {"value": "15", "label": "Burdur"},
        {"value": "16", "label": "Bursa"},
        {"value": "17", "label": "Çanakkale"},
        {"value": "18", "label": "Çankırı"},
        {"value": "19", "label": "Çorum"},
        {"value": "20", "label": "Denizli"},
        {"value": "21", "label": "Diyarbakır"},
        {"value": "22", "label": "Edirne"},
        {"value": "23", "label": "Elazığ"},
        {"value": "24", "label": "Erzincan"},
        {"value": "25", "label": "Erzurum"},
        {"value": "26", "label": "Eskişehir"},
        {"value": "27", "label": "Gaziantep"},
        {"value": "28", "label": "Giresun"},
        {"value": "29", "label": "Gümüşhane"},
        {"value": "30", "label": "Hakkâri"},
        {"value": "31", "label": "Hatay"},
        {"value": "32", "label": "Isparta"},
        {"value": "33", "label": "Mersin"},
        {"value": "34", "label": "İstanbul"},
        {"value": "35", "label": "İzmir"},
        {"value": "36", "label": "Kars"},
        {"value": "37", "label": "Kastamonu"},
        {"value": "38", "label": "Kayseri"},
        {"value": "39", "label": "Kırklareli"},
        {"value": "40", "label": "Kırşehir"},
        {"value": "41", "label": "Kocaeli"},
        {"value": "42", "label": "Konya"},
        {"value": "43", "label": "Kütahya"},
        {"value": "44", "label": "Malatya"},
        {"value": "45", "label": "Manisa"},
        {"value": "46", "label": "Kahramanmaraş"},
        {"value": "47", "label": "Mardin"},
        {"value": "48", "label": "Muğla"},
        {"value": "49", "label": "Muş"},
        {"value": "50", "label": "Nevşehir"},
        {"value": "51", "label": "Niğde"},
        {"value": "52", "label": "Ordu"},
        {"value": "53", "label": "Rize"},
        {"value": "54", "label": "Sakarya"},
        {"value": "55", "label": "Samsun"},
        {"value": "56", "label": "Siirt"},
        {"value": "57", "label": "Sinop"},
        {"value": "58", "label": "Sivas"},
        {"value": "59", "label": "Tekirdağ"},
        {"value": "60", "label": "Tokat"},
        {"value": "61", "label": "Trabzon"},
        {"value": "62", "label": "Tunceli"},
        {"value": "63", "label": "Şanlıurfa"},
        {"value": "64", "label": "Uşak"},
        {"value": "65", "label": "Van"},
        {"value": "66", "label": "Yozgat"},
        {"value": "67", "label": "Zonguldak"},
        {"value": "68", "label": "Aksaray"},
        {"value": "69", "label": "Bayburt"},
        {"value": "70", "label": "Karaman"},
        {"value": "71", "label": "Kırıkkale"},
        {"value": "72", "label": "Batman"},
        {"value": "73", "label": "Şırnak"},
        {"value": "74", "label": "Bartın"},
        {"value": "75", "label": "Ardahan"},
        {"value": "76", "label": "Iğdır"},
        {"value": "77", "label": "Yalova"},
        {"value": "78", "label": "Karabük"},
        {"value": "79", "label": "Kilis"},
        {"value": "80", "label": "Osmaniye"},
        {"value": "81", "label": "Düzce"},
    ]   

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
                user.country = form.cleaned_data['country'] 
                user.city = form.cleaned_data['city']
                user.district = form.cleaned_data['district']
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
            'address': request.user.address,
            'country': request.user.country,
            'city': request.user.city,
            'district': request.user.district,
        })

    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
        'form':form,
        'city_options': city_options,

        # Navbardaki Sepet Kısmında adet ve fiyat göstermek için
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi

    }
    return render(request, 'hesabim.html', context)


@login_required
def new_password(request):
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

    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,

        # Navbardaki Sepet Kısmında adet ve fiyat göstermek için
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi
    }

    if request.method == 'POST':
        old_password = request.POST['oldpassword']
        new_password = request.POST['password']
        confirm_password = request.POST['repassword']

        # Eski parolayı kontrol et
        if not request.user.check_password(old_password):
            messages.error(request, 'Eski parolayı yanlış girdiniz.')
            return redirect('new_password')

        # Yeni parolaların eşleştiğini kontrol et
        if new_password != confirm_password:
            messages.error(request, 'Yeni parolalar eşleşmiyor.')
            return redirect('new_password')

        # Parola karmaşıklığını kontrol et
        if not re.search(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', new_password):
            messages.error(request, 'Parola en az 8 karakter uzunluğunda, en az bir büyük harf, bir küçük harf ve bir sayı içermelidir.')
            return redirect('new_password')

        # Yeni parolayı güncelle
        user = request.user
        user.set_password(new_password)
        user.save()

        # Oturum kimliğini güncelle
        update_session_auth_hash(request, user)

        messages.success(request, 'Parolanız başarıyla güncellendi.')
        return redirect('new_password')

    return render(request, 'new_password.html', context)

