from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
from decimal import Decimal
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.db.models import Count
from userapp.forms import UserProfileForm
from userapp.models import MyUser
from datetime import datetime
from django.http import Http404
from django.contrib.auth.decorators import login_required
import time
from django.utils import timezone
#iyizipay importlar
import iyzipay
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
import pprint


#ip adresi çekme
def get_public_ip():
    try:
        response = requests.get('https://api64.ipify.org?format=json')
        data = response.json()
        return data['ip']
    except Exception as e:
        print("IP alınamadı:", e)
        return None
ip_address = get_public_ip()

# Create your views here.

#iyizipay 1

api_key = 'sandbox-mDxD5xa2K87j1qVrSZWuuZePxuQ4rAsP'
secret_key = 'sandbox-usRpErugCXKrEp2qFJV0fBFh3URAILWq'
base_url = 'sandbox-api.iyzipay.com'


options = {
    'api_key': api_key,
    'secret_key': secret_key,
    'base_url': base_url
}
sozlukToken = list()


#iyizipay viewsleri

def prepare_basket_items(siparis_urunler):
    prepared_items = []
    
    for siparis_urun in siparis_urunler:
        urun = siparis_urun.urun
        toplam_fiyat = siparis_urun.toplam_fiyat()
        prepared_item = {
            'id': urun.stokKodu,
            'name': urun.isim,
            'category1': urun.kategori,
            'category2': urun.kategori,
            'itemType': 'PHYSICAL',  # Varsayılan olarak fiziksel ürün
            'price': str(toplam_fiyat),  # Fiyatı string olarak çevir / buraya birim fiyat geliyordu. Toplam yaptık. Ama her ürün için bir item açılması lazım. Yani aynı model üründen 2 adet oldu mu 2 adet item oluşması gerekli. Bakılacak, unutma !!
        }
        prepared_items.append(prepared_item)

        print(f"Ürün Adı: {prepared_item['name']}, Fiyat: {prepared_item['price']}")
    
    return prepared_items





# SiparisUrun objelerini alın
siparis_urunler = SiparisUrun.objects.all()

# prepare_basket_items fonksiyonunu kullanarak basket_items listesini doldurun
basket_items = prepare_basket_items(siparis_urunler)








def payment(request):
    context = dict()
    odemeler = Siparis.objects.filter(user=request.user, odeme_bilgisi=False).order_by('-pk').first()
    siparis_urunler = SiparisUrun.objects.filter(siparis=odemeler)
    turkey_timezone = timezone.get_current_timezone()
    ip_address = get_public_ip()

    


    buyer={
        'id': odemeler.user.id,  #'BY789'
        'name': odemeler.teslimat_bilgileri_adi,
        'surname': odemeler.teslimat_bilgileri_soyadi,
        'gsmNumber': odemeler.teslimat_bilgileri_telefon,
        'email': odemeler.teslimat_bilgileri_email,
        'identityNumber': '98756487512',
        'lastLoginDate': odemeler.user.last_login.astimezone(turkey_timezone).strftime('%Y-%m-%d %H:%M:%S'),
        'registrationDate': odemeler.user.date_joined.astimezone(turkey_timezone).strftime('%Y-%m-%d %H:%M:%S'),
        'registrationAddress': odemeler.teslimat_bilgileri_adres,
        'ip': ip_address, #burayı çekmiyor olabilir
        'city': odemeler.teslimat_bilgileri_sehir,
        'country': odemeler.teslimat_bilgileri_ulke,
        # 'zipCode': '34732' zorunlu değil
    }

    address={
        'contactName': f'{odemeler.teslimat_bilgileri_adi} {odemeler.teslimat_bilgileri_soyadi}',
        'city': odemeler.teslimat_bilgileri_sehir,
        'country': odemeler.teslimat_bilgileri_ulke,
        'address': odemeler.teslimat_bilgileri_adres,
        # 'zipCode': '34732' zorunlu değil
    }

    

    # basket_items=[
    #     {
    #         'id': 'BI101',
    #         'name': 'Binocular',
    #         'category1': 'Collectibles',
    #         'category2': 'Accessories',
    #         'itemType': 'PHYSICAL',
    #         'price': '0.3' #sanırım buraların toplamı request te bulunan paidprice ile eşit olacak
    #     },
    #     {
    #         'id': 'BI102',
    #         'name': 'Game code',
    #         'category1': 'Game',
    #         'category2': 'Online Game Items',
    #         'itemType': 'VIRTUAL',
    #         'price': '0.5' #sanırım buraların toplamı request te bulunan paidprice ile eşit olacak
    #     },
    #     {
    #         'id': 'BI103',
    #         'name': 'Usb',
    #         'category1': 'Electronics',
    #         'category2': 'Usb / Cable',
    #         'itemType': 'PHYSICAL',
    #         'price': '0.2' #sanırım buraların toplamı request te bulunan paidprice ile eşit olacak
    #     }
    # ]

    basket_items = prepare_basket_items(siparis_urunler)

    print(basket_items)

    request={
        'locale': 'tr',
        'conversationId': '123456789', #sepet id
        'price': str(odemeler.toplam_fiyat),
        'paidPrice': str(odemeler.toplam_fiyat),
        'currency': 'TRY',
        'basketId': 'B67832',
        'paymentGroup': 'PRODUCT',
        "callbackUrl": "http://127.0.0.1:8000/result/",
        "enabledInstallments": ['2', '3', '6', '9'],
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items,
        # 'debitCardAllowed': True
    }

    checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(request, options)

    # print(checkout_form_initialize.read().decode('utf-8'))
    page = checkout_form_initialize
    header = {'Content-Type': 'application/json'}
    content = checkout_form_initialize.read().decode('utf-8')
    json_content = json.loads(content)
    print(type(json_content))
    print(json_content["checkoutFormContent"])
    print("************************")
    print(json_content["token"])
    print("************************")
    sozlukToken.append(json_content["token"])
    return HttpResponse(json_content["checkoutFormContent"])


@require_http_methods(['POST'])
@csrf_exempt
def result(request):
    context = dict()

    url = request.META.get('index')


    request = {
        'locale': 'tr',
        'conversationId': '123456789',
        'token': sozlukToken[0]
    }
    checkout_form_result = iyzipay.CheckoutForm().retrieve(request, options)
    print("************************")
    print(type(checkout_form_result))
    result = checkout_form_result.read().decode('utf-8')
    print("************************")
    print(sozlukToken[0])   # Form oluşturulduğunda 
    print("************************")
    print("************************")
    sonuc = json.loads(result, object_pairs_hook=list)
    #print(sonuc[0][1])  # İşlem sonuç Durumu dönüyor
    #print(sonuc[5][1])   # Test ödeme tutarı
    print("************************")
    for i in sonuc:
        print(i)
    print("************************")
    print(sozlukToken)
    print("************************")
    if sonuc[0][1] == 'success':
        context['success'] = 'Başarılı İŞLEMLER'
        return HttpResponseRedirect(reverse('success'), context)

    elif sonuc[0][1] == 'failure':
        context['failure'] = 'Başarısız'
        return HttpResponseRedirect(reverse('failure'), context)

    return HttpResponse(url)

def success(request):
    context = dict()
    context['success'] = 'İşlem Başarılı'
    messages.success(request, 'İşlem Başarılı')

    template = 'ok.html'
    response = render(request, template, context)

    # 5 saniye bekleyip sonra ana sayfaya yönlendirme
    response['refresh'] = '5;url=/'
    
    return response

def fail(request):
    context = dict()
    context['fail'] = 'İşlem Başarısız'
    messages.success(request, 'İşlem Başarılı')

    template = 'fail.html'
    return render(request, template, context)
    # return redirect('index')

#-------------iyizipay son------------


def index(request):
    slogan = Slogan.objects.first()
    anakategori = Anakategori.objects.all()
    urunler = Urun.objects.all()
    wrapperOne = Wrapperone.objects.all()
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
        'slogan': slogan,
        'anakategori' : anakategori,
        'urunler' : urunler,
        'wrapperone' : wrapperOne,
        'footer' : footer,
        'social_media' : socail_media,

        # Navbardaki Sepet Kısmında adet ve fiyat göstermek için
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi

    }
    return render(request, 'index.html', context)

def allProduct(request):
    urunler = Urun.objects.all()
    urun_sayisi = urunler.values('isim').annotate(urun_sayisi=Count('isim')) #Filtrede ürün sayısı göstermek için
    renk_sayisi = urunler.values('urunRengi').annotate(renk_sayisi=Count('urunRengi')) #Filtrede renk sayısı göstermek için
    kaplama_sayisi = urunler.values('ayakKaplama').annotate(kaplama_sayisi=Count('ayakKaplama')) #Filtrede kaplama sayısı göstermek için
    indirimli_urun_sayisi = urunler.filter(indirimli_fiyat__isnull=False).count() #Filtrede indirimli öğe sayısı göstermek için
    anakategori = Anakategori.objects.all()
    wrapperOne = Wrapperone.objects.all()
    sort_option = request.GET.get('sort_option')
    search_query = request.GET.get('search_query')
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

    if search_query:
        urunler = urunler.filter(
            Q(isim__icontains=search_query) |
            Q(kategori__icontains=search_query) |
            Q(urunRengi__icontains=search_query) |
            Q(stokKodu__icontains=search_query) |
            Q(aciklama__icontains=search_query)
        )

    if sort_option == 'asc':
        if urunler.filter(indirimli_fiyat__isnull=False).exists():
            urunler = urunler.annotate(
                indirimli_fiyat_sira=Coalesce('indirimli_fiyat', 'fiyat')
            ).order_by('indirimli_fiyat_sira')
        else:
            urunler = urunler.order_by('fiyat')
    elif sort_option == 'desc':
        if urunler.filter(indirimli_fiyat__isnull=False).exists():
            urunler = urunler.annotate(
                indirimli_fiyat_sira=Coalesce('indirimli_fiyat', 'fiyat')
            ).order_by('-indirimli_fiyat_sira')
        else:
            urunler = urunler.order_by('-fiyat')
    
    ayak_kaplama = request.GET.get('ayak_kaplama')  # Ayak kaplaması filtresi için parametreyi al
    if ayak_kaplama:
        urunler = urunler.filter(ayakKaplama__iexact=ayak_kaplama)  # Ayak kaplaması filtresini uygula
    indirimli_urunler = request.GET.get('indirimli_urunler')  # İndirimli ürünler filtresi için parametreyi al
    if indirimli_urunler:
        urunler = urunler.filter(indirimli_fiyat__isnull=False)  # İndirimli ürünler filtresini uygula
    min_fiyat = request.GET.get('min_fiyat')  # Minimum fiyat parametresini al
    max_fiyat = request.GET.get('max_fiyat')  # Maksimum fiyat parametresini al
    if min_fiyat and max_fiyat:
        urunler = urunler.filter(fiyat__gte=min_fiyat, fiyat__lte=max_fiyat)  # Fiyat aralığı filtresini uygula
    

    context = {
        'anakategori': anakategori,
        'urunler': urunler,
        'wrapperone' : wrapperOne,
        'sort_option': sort_option,
        'search_query': search_query,
        'footer' : footer,
        'social_media' : socail_media,
        'urun_sayisi': urun_sayisi, #filtrede ürün sayısı göstermek için 
        'renk_sayisi': renk_sayisi, #filtrede renk sayısı göstermek için
        'kaplama_sayisi': kaplama_sayisi, #filtrede kaplama sayısı göstermek için
        'indirimli_urun_sayisi': indirimli_urun_sayisi, #filtrede indirimli öğe sayısı göstermek için

        # Navbardaki Sepet Kısmında adet ve fiyat göstermek için
        'sepetim': sepetim,
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi,
        'urun_bulunamadi': False,
    }
    
    if min_fiyat and max_fiyat and not urunler.exists():
        context['urun_bulunamadi'] = True

    if search_query and not urunler.exists():
        context['no_results'] = True

    return render(request, 'all-product.html', context)

def category(request,categoryName):
    # urunler = Urun.objects.filter(kategori=categoryName)
    try:
        
        valid_categories = [urun.kategori for urun in Urun.objects.all()]  
        if categoryName not in valid_categories:
            raise Http404("Böyle bir kategori bulunamadı.")
        
        urunler = Urun.objects.filter(kategori=categoryName)
    except Urun.DoesNotExist:
        raise Http404("Böyle bir kategori bulunamadı.")
    
    urun_sayisi = urunler.values('isim').annotate(urun_sayisi=Count('isim')) #Filtrede ürün sayısı göstermek için
    renk_sayisi = urunler.values('urunRengi').annotate(renk_sayisi=Count('urunRengi')) #Filtrede renk sayısı göstermek için
    kaplama_sayisi = urunler.values('ayakKaplama').annotate(kaplama_sayisi=Count('ayakKaplama')) #Filtrede kaplama sayısı göstermek için
    indirimli_urun_sayisi = urunler.filter(indirimli_fiyat__isnull=False).count() #Filtrede indirimli öğe sayısı göstermek için
    anakategori = Anakategori.objects.all()
    wrapperOne = Wrapperone.objects.all()
    sort_option = request.GET.get('sort_option')
    search_query = request.GET.get('search_query')
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




    if search_query:
        urunler = urunler.filter(
            Q(isim__icontains=search_query) |
            Q(kategori__icontains=search_query) |
            Q(urunRengi__icontains=search_query) |
            Q(stokKodu__icontains=search_query) |
            Q(aciklama__icontains=search_query)
        )

    if sort_option == 'asc':
        if urunler.filter(indirimli_fiyat__isnull=False).exists():
            urunler = urunler.annotate(
                indirimli_fiyat_sira=Coalesce('indirimli_fiyat', 'fiyat')
            ).order_by('indirimli_fiyat_sira')
        else:
            urunler = urunler.order_by('fiyat')
    elif sort_option == 'desc':
        if urunler.filter(indirimli_fiyat__isnull=False).exists():
            urunler = urunler.annotate(
                indirimli_fiyat_sira=Coalesce('indirimli_fiyat', 'fiyat')
            ).order_by('-indirimli_fiyat_sira')
        else:
            urunler = urunler.order_by('-fiyat')
    
    ayak_kaplama = request.GET.get('ayak_kaplama')  # Ayak kaplaması filtresi için parametreyi al
    if ayak_kaplama:
        urunler = urunler.filter(ayakKaplama__iexact=ayak_kaplama)  # Ayak kaplaması filtresini uygula
    indirimli_urunler = request.GET.get('indirimli_urunler')  # İndirimli ürünler filtresi için parametreyi al
    if indirimli_urunler:
        urunler = urunler.filter(indirimli_fiyat__isnull=False)  # İndirimli ürünler filtresini uygula
    min_fiyat = request.GET.get('min_fiyat')  # Minimum fiyat parametresini al
    max_fiyat = request.GET.get('max_fiyat')  # Maksimum fiyat parametresini al
    if min_fiyat and max_fiyat:
        urunler = urunler.filter(fiyat__gte=min_fiyat, fiyat__lte=max_fiyat)  # Fiyat aralığı filtresini uygula


    context = {
        'anakategori' : anakategori,
        'urunler' : urunler,
        'wrapperone' : wrapperOne,
        'kategori': categoryName,
        'sort_option': sort_option,
        'search_query': search_query,
        'footer' : footer,
        'social_media' : socail_media,
        'urun_sayisi': urun_sayisi, #filtrede ürün sayısı göstermek için 
        'renk_sayisi': renk_sayisi, #filtrede renk sayısı göstermek için
        'kaplama_sayisi': kaplama_sayisi, #filtrede kaplama sayısı göstermek için
        'indirimli_urun_sayisi': indirimli_urun_sayisi, #filtrede indirimli öğe sayısı göstermek için

        # Navbardaki aktif menüyü göstermek için
        'categoryName': categoryName,

        # Navbardaki Sepet Kısmında adet ve fiyat göstermek için
        'sepetim': sepetim,
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi,

    }

    if min_fiyat and max_fiyat and not urunler.exists():
        context['urun_bulunamadi'] = True

    if search_query and not urunler.exists():
        context['no_results'] = True

    return render(request, 'category.html', context)

def productDetail(request, urunId):
    urunum = Urun.objects.get(id = urunId)
    ayniKategoridekiUrunler = Urun.objects.filter(kategori=urunum.kategori).exclude(id=urunum.id)
    anakategori = Anakategori.objects.all()
    wrapperOne = Wrapperone.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()

    # SEPETE EKLEME
    if request.method == 'POST':
        if request.user.is_authenticated:
            urunId = request.POST['urunId']
            adet = request.POST['adet']
            adet = int(adet)
            #eklenecek ürün
            urunum = Urun.objects.get(id = urunId)

            # İndirimli fiyatı hesapla
            fiyat = urunum.fiyat
            if urunum.indirimli_fiyat:
                fiyat = urunum.indirimli_fiyat

            if Sepet.objects.filter(user = request.user, urun = urunum).exists():
                sepetim = Sepet.objects.get(user = request.user, urun=urunum)
                sepetim.adet += adet
                sepetim.toplam = urunum.fiyat * sepetim.adet
                sepetim.save()
                messages.success(request, 'Ürün Sepette Güncellendi')
                
            else:
                sepetim = Sepet.objects.create(
                    urun = urunum,
                    user = request.user,
                    adet = adet,
                    toplam=fiyat * adet  # İndirimli fiyatı kullan
                )
                sepetim.save()
                messages.success(request, 'Ürün Sepete Eklendi')
                
            return redirect('product', urunId=urunId)
        else:
            messages.error(request, 'Giriş Yapmanız Gerekiyor')
            return redirect('login')
        
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
        'urun' : urunum,
        'wrapperone' : wrapperOne,
        'ayniKategoridekiUrunler' : ayniKategoridekiUrunler,
        'footer' : footer,
        'social_media' : socail_media,

        # Navbardaki Sepet Kısmında adet ve fiyat göstermek için
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi,
        
    }


    return render(request, 'product-detail.html', context)

def aboutUs(request):
    anakategori = Anakategori.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    hakkimizda = Hakkimizda.objects.first()

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
        'hakkimizda' : hakkimizda,

        # Navbardaki Sepet Kısmında adet ve fiyat göstermek için
        'sepetim': sepetim,
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi
    }
    return render(request, 'about-us.html', context)

def contactUs(request):
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
        'sepetim': sepetim,
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi
    }
    return render(request, 'contact-us.html', context)

def sepet(request):
    anakategori = Anakategori.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    user = request.user
    sepetim = Sepet.objects.filter(user=user)
    toplam_tutar = Decimal('0.00')
    toplam_urun_sayisi = 0
    kdv = int(toplam_tutar * Decimal('0.2'))
    araToplam = int(toplam_tutar - Decimal(kdv))




    if request.method == 'POST':
        urunId = request.POST['urunId']
        sepet = Sepet.objects.get(id=urunId)

        # if 'guncelle' in request.POST: #Formda name'i guncelle butonu açılır tekrar kullanılmak istenirse
        #     yeniAdet = request.POST['yeniAdet']

        #     if yeniAdet > '0':
        #         sepet.adet = yeniAdet
        #         if sepet.urun.indirimli_fiyat:
        #             sepet.toplam = sepet.urun.indirimli_fiyat * int(yeniAdet)
        #         else:
        #             sepet.toplam = sepet.urun.fiyat * int(yeniAdet)
                
        #         sepet.save()
        #         messages.success(request, f'{sepet.urun.isim} Ürününün Adedi Güncellendi')
        #     else:
        #         messages.error(request, 'Geçersiz ürün adedi. Lütfen pozitif bir değer girin.')
        #     return redirect('sepet')

        if 'artir' in request.POST:
            yeniAdet = request.POST['yeniAdet']

            if yeniAdet > '0':
                sepet.adet = yeniAdet
                if sepet.urun.indirimli_fiyat:
                    sepet.toplam = sepet.urun.indirimli_fiyat * int(yeniAdet)
                else:
                    sepet.toplam = sepet.urun.fiyat * int(yeniAdet)
                
                sepet.save()
                messages.success(request, f'{sepet.urun.isim} Ürününün Adedi Güncellendi')
            else:
                messages.error(request, 'Geçersiz ürün adedi. Lütfen pozitif bir değer girin.')
            return redirect('sepet')
        
        elif 'azalt' in request.POST:
            yeniAdet = request.POST['yeniAdet']

            if yeniAdet > '0':
                sepet.adet = yeniAdet
                if sepet.urun.indirimli_fiyat:
                    sepet.toplam = sepet.urun.indirimli_fiyat * int(yeniAdet)
                else:
                    sepet.toplam = sepet.urun.fiyat * int(yeniAdet)
                
                sepet.save()
                messages.success(request, f'{sepet.urun.isim} Ürününün Adedi Güncellendi')
            else:
                messages.error(request, 'Geçersiz ürün adedi. Lütfen pozitif bir değer girin.')
            return redirect('sepet')

        else:
            sepet.delete()
            messages.success(request, 'Ürün sepetten kaldırıldı.')
            return redirect('sepet')

        
        

    for sepet in sepetim:
        toplam_tutar += sepet.hesapla_toplam()
        toplam_urun_sayisi += sepet.adet
    
    kdv = toplam_tutar * Decimal('0.2')
    araToplam = toplam_tutar - kdv

    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
        'sepetim': sepetim,
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi,
        'kdv': kdv,
        'araToplam': araToplam
    }
    return render(request, 'sepet.html', context)



def loading_page(request):
    return render(request, 'includes/_loading.html')

def yardim(request):
    anakategori = Anakategori.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    uyelikMetni = Uyelikmetni.objects.first()
    kvkkMetni = Kvkkmetni.objects.first()
    mesafeli_satis_sozlesmesi = Mesafelisatisozlesmesi.objects.first()
    gizlilikSozlesmesi = Gizliliksozlesmesi.objects.first()
    iptalveiade = Iptalveiade.objects.first()
    kurulum = Kurulum.objects.first()

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
        'uyelikMetni' : uyelikMetni,
        'kvkkMetni' : kvkkMetni,
        'mesafeli_satis_sozlesmesi' : mesafeli_satis_sozlesmesi,
        'gizlilikSozlesmesi' : gizlilikSozlesmesi,
        'iptalveiade' : iptalveiade,
        'kurulum' : kurulum,

        # Navbardaki Sepet Kısmında adet ve fiyat göstermek için
        'sepetim': sepetim,
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi
    }
    return render(request, 'yardim.html', context)

def teslimat(request):
    anakategori = Anakategori.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()

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

    # if not request.META.get('HTTP_REFERER') or '/sepet/' not in request.META.get('HTTP_REFERER'):
    #     # Eğer sayfa refereri sepet sayfasına değilse veya referer yoksa, buraya erişim engellenir
    #     return redirect('sepet')

    user = request.user
    toplam_tutar = Decimal('0.00')
    toplam_urun_sayisi = 0


    if user.is_authenticated:  # Kullanıcı girişi yapılmışsa
        sepetim = Sepet.objects.filter(user=user)
        for sepet in sepetim:
            toplam_tutar += sepet.hesapla_toplam()
            toplam_urun_sayisi += sepet.adet
        kdv = toplam_tutar * Decimal('0.2')
        araToplam = toplam_tutar - kdv
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
                messages.success(request, 'Teslimat Bilgileriniz Güncellendi.')
                return redirect('odemebilgilerikontrol')
            

        #* burası sipariş takip fonksiyonu önemli. Buraya gelecek bilgileride çekip bu fonksiyonu başka sayfada yazacağız
        # if 'odeme' in request.POST:
            
        #     siparis = Siparis.objects.create(
        #         user=user,
        #         toplam_fiyat=toplam_tutar,
        #         odeme_bilgisi=False,
        #         gonderim_bilgisi=False,
        #         teslimat_bilgileri_adi = user.first_name,
        #         teslimat_bilgileri_soyadi = user.last_name,
        #         teslimat_bilgileri_telefon = user.phone,
        #         teslimat_bilgileri_adres = user.address,
        #         teslimat_bilgileri_ulke = user.country,
        #         teslimat_bilgileri_sehir = user.city,
        #         teslimat_bilgileri_ilce = user.district

        #     )

            
        #     for sepet in sepetim:
        #         SiparisUrun.objects.create(
        #             siparis=siparis,
        #             urun=sepet.urun,
        #             urun_stok_kodu=sepet.urun.stokKodu,
        #             adet=sepet.adet,
        #             birim_fiyat=sepet.urun.fiyat if not sepet.urun.indirimli_fiyat else sepet.urun.indirimli_fiyat,
        #             urun_resmi=sepet.urun.urunresmi
        #         )
            
        #     sepetim.delete()
            
        #     messages.success(request, 'Siparişiniz alındı. Ödeme yapabilirsiniz.')
        #     return redirect('teslimat')

        
            
        

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
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi,
        'kdv': kdv,
        'araToplam': araToplam,
        'form':form,
        'city_options': city_options,
    }
    return render(request, 'teslimat-bilgileri.html', context)

def odemebilgileriKontrol(request):
    anakategori = Anakategori.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    form = UserProfileForm

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

    # if not request.META.get('HTTP_REFERER') or '/sepet/' not in request.META.get('HTTP_REFERER'):
    #     # Eğer sayfa refereri sepet sayfasına değilse veya referer yoksa, buraya erişim engellenir
    #     return redirect('sepet')

    user = request.user
    toplam_tutar = Decimal('0.00')
    toplam_urun_sayisi = 0


    if user.is_authenticated:  # Kullanıcı girişi yapılmışsa
        sepetim = Sepet.objects.filter(user=user)
        for sepet in sepetim:
            toplam_tutar += sepet.hesapla_toplam()
            toplam_urun_sayisi += sepet.adet
        kdv = toplam_tutar * Decimal('0.2')
        araToplam = toplam_tutar - kdv
    else:  # Kullanıcı girişi yapılmamışsa, boş bir sepet listesi oluştur
        sepetim = []


    #* burası sipariş takip fonksiyonu önemli. Buraya gelecek bilgileride çekip bu fonksiyonu başka sayfada yazacağız
    if 'odeme' in request.POST:
        
        siparis = Siparis.objects.create(
            user=user,
            toplam_fiyat=toplam_tutar,
            odeme_bilgisi=False,
            teslimat_bilgileri_adi = user.first_name,
            teslimat_bilgileri_soyadi = user.last_name,
            teslimat_bilgileri_telefon = user.phone,
            teslimat_bilgileri_adres = user.address,
            teslimat_bilgileri_ulke = user.country,
            teslimat_bilgileri_sehir = user.city,
            teslimat_bilgileri_ilce = user.district,
            teslimat_bilgileri_email = user.email

        )

        
        for sepet in sepetim:
            SiparisUrun.objects.create(
                siparis=siparis,
                urun=sepet.urun,
                urun_stok_kodu=sepet.urun.stokKodu,
                adet=sepet.adet,
                birim_fiyat=sepet.urun.fiyat if not sepet.urun.indirimli_fiyat else sepet.urun.indirimli_fiyat,
                urun_resmi=sepet.urun.urunresmi
            )
        
        sepetim.delete()
        
        messages.success(request, 'Siparişiniz alındı. Ödeme yapabilirsiniz.')
        return redirect('payment')

    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi,
        'kdv': kdv,
        'araToplam': araToplam,
        'form':form,
        'city_options': city_options,
    }
    return render(request, 'odeme-bilgileri-kontrol.html', context)

@login_required
def siparislerim(request):
    user = request.user
    siparisler = Siparis.objects.filter(user=user).order_by('-satinalma_tarihi')
    anakategori = Anakategori.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    form = UserProfileForm

    


    if request.method == 'POST':
        siparis_id = request.POST.get('siparis_id')  # Formdan gelen siparis_id
        siparis = Siparis.objects.get(id=siparis_id)
        
        if 'siparis_iptal_btn' in request.POST:
            if not siparis.kargoya_verildi and not siparis.siparis_iptal:
                siparis.siparis_iptal = True
                siparis.save()
                messages.success(request, 'Siparişiniz iptal edildi.')
                return redirect('siparislerim')

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

    # if not request.META.get('HTTP_REFERER') or '/sepet/' not in request.META.get('HTTP_REFERER'):
    #     # Eğer sayfa refereri sepet sayfasına değilse veya referer yoksa, buraya erişim engellenir
    #     return redirect('sepet')

    toplam_tutar = Decimal('0.00')
    toplam_urun_sayisi = 0
    kdv = Decimal('0.00')
    araToplam = Decimal('0.00')


    siparis = None  # siparis değişkenini döngü dışında tanımladık

    for siparis in siparisler:
        try:
            siparis.toplam_adet = sum(su.adet for su in siparis.siparisurun_set.all())
        except Siparis.DoesNotExist:
            # Sipariş silindi, böylece üzerinde işlem yapamayız
            pass



    if user.is_authenticated:  # Kullanıcı girişi yapılmışsa
        sepetim = Sepet.objects.filter(user=user)
        for sepet in sepetim:
            toplam_tutar += sepet.hesapla_toplam()
            toplam_urun_sayisi += sepet.adet
        kdv = toplam_tutar * Decimal('0.2')
        araToplam = toplam_tutar - kdv
    else:  # Kullanıcı girişi yapılmamışsa, boş bir sepet listesi oluştur
        sepetim = []



    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi,
        'kdv': kdv,
        'araToplam': araToplam,
        'form':form,
        'city_options': city_options,
        'siparisler': siparisler,
        'siparis': siparis
    }
    return render(request, 'siparislerim.html', context)

def view_404(request, exception):
    return redirect('/')