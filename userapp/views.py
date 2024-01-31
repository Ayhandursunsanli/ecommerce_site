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
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import PasswordChangeForm


def is_valid_phone_number(phone_number, country_code):
    try:
        parsed_number = phonenumbers.parse(phone_number, country_code)
        return phonenumbers.is_valid_number(parsed_number)
    except Exception as e:
        print("Telefon numarası analizi sırasında bir hata oluştu:", e)
        return False


class CustomAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)

def login_request(request):
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    anakategori = Anakategori.objects.all()
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Hoşgeldin {request.user.first_name}.')
                    return redirect('index')
                else:
                    messages.error(request, 'Hesabınız aktif değil. Lütfen e-posta onayınızı tamamlayın.')
                    return redirect('login')
            else:
                messages.error(request, 'Kullanıcı adı veya parola hatalı')
                return redirect('login')
    else:
        form = CustomAuthenticationForm()

    context = {
        'form': form,
        'anakategori': anakategori,
        'footer': footer,
        'social_media': socail_media,
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
        return redirect('login')

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

    try:
        if email.send():
            messages.success(request, f"Sayın {user.username}, lütfen e-postanızdaki {to_email} gelen kutusuna gidin ve kaydı onaylamak için alınan aktivasyon bağlantısına tıklayın.")
        else:
            messages.error(request, f"Sayın {user.username}, e-postaya aktivasyon bağlantısı gönderilirken bir hata oluştu.")
    except Exception as e:
        messages.error(request, f"E-posta gönderilirken bir hata oluştu: {e}")

    return redirect('login')


def register(request):
    anakategori = Anakategori.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    uyelikMetni = Uyelikmetni.objects.first()
    kvkkMetni = Kvkkmetni.objects.first()

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
            return render(request, 'register.html', {
                'error': 'Kullanıcı adı, e-posta, üyelik sözleşmesi ve kişisel veri aydınlatma metni kabul edilmelidir.',
                'username': username,
                'email': email,
                'firstname': firstname,
                'lastname': lastname,
                'phone': phone,
                'anakategori': anakategori,
                'footer': footer,
                'social_media': socail_media,
                'uyelikMetni': uyelikMetni,
                'kvkkMetni': kvkkMetni
            })

        if ' ' in username or re.search(r'[ğüşıöçĞÜŞİÖÇ]', username):
            return render(request, 'register.html', {
                'error': 'Kullanıcı adı boşluk içeremez ve Türkçe karakterler içeremez.',
                'username': username,
                'email': email,
                'firstname': firstname,
                'lastname': lastname,
                'phone': phone,
                'anakategori': anakategori,
                'footer': footer,
                'social_media': socail_media,
                'uyelikMetni': uyelikMetni,
                'kvkkMetni': kvkkMetni
            })

        if password == repassword:
            if MyUser.objects.filter(username=username).exists():
                return render(request, 'register.html', {
                    'error': 'Bu kullanıcı adı daha önce alınmış',
                    'username': username,
                    'email': email,
                    'firstname': firstname,
                    'lastname': lastname,
                    'phone': phone,
                    'anakategori': anakategori,
                    'footer': footer,
                    'social_media': socail_media,
                    'uyelikMetni': uyelikMetni,
                    'kvkkMetni': kvkkMetni
                })
            else:
                if MyUser.objects.filter(email=email).exists():
                    return render(request, 'register.html', {
                        'error': 'Bu email daha önce alınmış',
                        'username': username,
                        'email': email,
                        'firstname': firstname,
                        'lastname': lastname,
                        'phone': phone,
                        'anakategori': anakategori,
                        'footer': footer,
                        'social_media': socail_media,
                        'uyelikMetni': uyelikMetni,
                        'kvkkMetni': kvkkMetni
                    })
                else:
                    if not re.search(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', password):
                        return render(request, 'register.html', {
                            'error': 'Parola en az 8 karakter uzunluğunda olmalı ve en az bir büyük harf, bir küçük harf ve bir rakam içermelidir.',
                            'username': username,
                            'email': email,
                            'firstname': firstname,
                            'lastname': lastname,
                            'phone': phone,
                            'anakategori': anakategori,
                            'footer': footer,
                            'social_media': socail_media,
                            'uyelikMetni': uyelikMetni,
                            'kvkkMetni': kvkkMetni
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
                            'uyelikMetni': uyelikMetni,
                            'kvkkMetni': kvkkMetni
                        })

                    if not is_valid_phone_number(phone, 'TR'):  # Telefon numarasını geçerlilik kontrolü yapmak için ülke kodunu uygun şekilde ayarlayın
                        return render(request, 'register.html', {
                            'error': 'Geçersiz telefon numarası',
                            'username': username,
                            'email': email,
                            'firstname': firstname,
                            'lastname': lastname,
                            'phone': phone,
                            'anakategori': anakategori,
                            'footer': footer,
                            'social_media': socail_media,
                            'uyelikMetni': uyelikMetni,
                            'kvkkMetni': kvkkMetni
                        })

                    # Kullanıcı kayıt işlemi buraya eklenecek
                    user = MyUser.objects.create_user(username=username, email=email, first_name=firstname, last_name=lastname, password=password, phone=phone)
                    user.is_active = False
                    user.save()
                    activateEmail(request, user, email)
                    return redirect('login')
        else:
            return render(request, 'register.html', {
                'error': 'Parolalar eşleşmiyor',
                'username': username,
                'email': email,
                'firstname': firstname,
                'lastname': lastname,
                'phone': phone,
                'anakategori': anakategori,
                'footer': footer,
                'social_media': socail_media,
                'uyelikMetni': uyelikMetni,
                'kvkkMetni': kvkkMetni
            })

    context = {
        'anakategori': anakategori,
        'footer': footer,
        'social_media': socail_media,
        'uyelikMetni': uyelikMetni,
        'kvkkMetni': kvkkMetni
    }
    return render(request, 'register.html', context)



def logout_request(request):
    logout(request)
    messages.success(request, "Başarıyla çıkış yaptınız.")
    return redirect('index')


def update_profile(request):

    city_options = [
        {"value": "Adana", "label": "Adana"},
        {"value": "Adıyaman", "label": "Adıyaman"},
        {"value": "Afyonkarahisar", "label": "Afyonkarahisar"},
        {"value": "Ağrı", "label": "Ağrı"},
        {"value": "Amasya", "label": "Amasya"},
        {"value": "Ankara", "label": "Ankara"},
        {"value": "Antalya", "label": "Antalya"},
        {"value": "Artvin", "label": "Artvin"},
        {"value": "Aydın", "label": "Aydın"},
        {"value": "Balıkesir", "label": "Balıkesir"},
        {"value": "Bilecik", "label": "Bilecik"},
        {"value": "Bingöl", "label": "Bingöl"},
        {"value": "Bitlis", "label": "Bitlis"},
        {"value": "Bolu", "label": "Bolu"},
        {"value": "Burdur", "label": "Burdur"},
        {"value": "Bursa", "label": "Bursa"},
        {"value": "Çanakkale", "label": "Çanakkale"},
        {"value": "Çankırı", "label": "Çankırı"},
        {"value": "Çorum", "label": "Çorum"},
        {"value": "Denizli", "label": "Denizli"},
        {"value": "Diyarbakır", "label": "Diyarbakır"},
        {"value": "Edirne", "label": "Edirne"},
        {"value": "Elazığ", "label": "Elazığ"},
        {"value": "Erzincan", "label": "Erzincan"},
        {"value": "Erzurum", "label": "Erzurum"},
        {"value": "Eskişehir", "label": "Eskişehir"},
        {"value": "Gaziantep", "label": "Gaziantep"},
        {"value": "Giresun", "label": "Giresun"},
        {"value": "Gümüşhane", "label": "Gümüşhane"},
        {"value": "Hakkâri", "label": "Hakkâri"},
        {"value": "Hatay", "label": "Hatay"},
        {"value": "Isparta", "label": "Isparta"},
        {"value": "Mersin", "label": "Mersin"},
        {"value": "İstanbul", "label": "İstanbul"},
        {"value": "İzmir", "label": "İzmir"},
        {"value": "Kars", "label": "Kars"},
        {"value": "Kastamonu", "label": "Kastamonu"},
        {"value": "Kayseri", "label": "Kayseri"},
        {"value": "Kırklareli", "label": "Kırklareli"},
        {"value": "Kırşehir", "label": "Kırşehir"},
        {"value": "Kocaeli", "label": "Kocaeli"},
        {"value": "Konya", "label": "Konya"},
        {"value": "Kütahya", "label": "Kütahya"},
        {"value": "Malatya", "label": "Malatya"},
        {"value": "Manisa", "label": "Manisa"},
        {"value": "Kahramanmaraş", "label": "Kahramanmaraş"},
        {"value": "Mardin", "label": "Mardin"},
        {"value": "Muğla", "label": "Muğla"},
        {"value": "Muş", "label": "Muş"},
        {"value": "Nevşehir", "label": "Nevşehir"},
        {"value": "Niğde", "label": "Niğde"},
        {"value": "Ordu", "label": "Ordu"},
        {"value": "Rize", "label": "Rize"},
        {"value": "Sakarya", "label": "Sakarya"},
        {"value": "Samsun", "label": "Samsun"},
        {"value": "Siirt", "label": "Siirt"},
        {"value": "Sinop", "label": "Sinop"},
        {"value": "Sivas", "label": "Sivas"},
        {"value": "Tekirdağ", "label": "Tekirdağ"},
        {"value": "Tokat", "label": "Tokat"},
        {"value": "Trabzon", "label": "Trabzon"},
        {"value": "Tunceli", "label": "Tunceli"},
        {"value": "Şanlıurfa", "label": "Şanlıurfa"},
        {"value": "Uşak", "label": "Uşak"},
        {"value": "Van", "label": "Van"},
        {"value": "Yozgat", "label": "Yozgat"},
        {"value": "Zonguldak", "label": "Zonguldak"},
        {"value": "Aksaray", "label": "Aksaray"},
        {"value": "Bayburt", "label": "Bayburt"},
        {"value": "Karaman", "label": "Karaman"},
        {"value": "Kırıkkale", "label": "Kırıkkale"},
        {"value": "Batman", "label": "Batman"},
        {"value": "Şırnak", "label": "Şırnak"},
        {"value": "Bartın", "label": "Bartın"},
        {"value": "Ardahan", "label": "Ardahan"},
        {"value": "Iğdır", "label": "Iğdır"},
        {"value": "Yalova", "label": "Yalova"},
        {"value": "Karabük", "label": "Karabük"},
        {"value": "Kilis", "label": "Kilis"},
        {"value": "Osmaniye", "label": "Osmaniye"},
        {"value": "Düzce", "label": "Düzce"},
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
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Oturum kimliğini güncelle
            messages.success(request, 'Parolanız başarıyla güncellendi.')
            return redirect('new_password')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'new_password.html', {'form': form, **context})


