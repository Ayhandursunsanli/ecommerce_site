from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
from decimal import Decimal

from django.db.models import Q


# Create your views here.

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
        urunler = urunler.order_by('fiyat')
    elif sort_option == 'desc':
        urunler = urunler.order_by('-fiyat')

    context = {
        'anakategori': anakategori,
        'urunler': urunler,
        'wrapperone' : wrapperOne,
        'sort_option': sort_option,
        'search_query': search_query,
        'footer' : footer,
        'social_media' : socail_media,

        # Navbardaki Sepet Kısmında adet ve fiyat göstermek için
        'sepetim': sepetim,
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi
    }

    if search_query and not urunler.exists():
        context['no_results'] = True

    return render(request, 'all-product.html', context)

def category(request,categoryName):
    urunler = Urun.objects.filter(kategori=categoryName)
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
        urunler = urunler.order_by('fiyat')
    elif sort_option == 'desc':
        urunler = urunler.order_by('-fiyat')


    context = {
        'anakategori' : anakategori,
        'urunler' : urunler,
        'wrapperone' : wrapperOne,
        'kategori': categoryName,
        'sort_option': sort_option,
        'search_query': search_query,
        'footer' : footer,
        'social_media' : socail_media,

        # Navbardaki aktif menüyü göstermek için
        'categoryName': categoryName,

        # Navbardaki Sepet Kısmında adet ve fiyat göstermek için
        'sepetim': sepetim,
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi,

    }

    if search_query and not urunler.exists():
        context['no_results'] = True

    return render(request, 'category.html',context)

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
            if Sepet.objects.filter(user = request.user, urun = urunum).exists():
                sepetim = Sepet.objects.get(user = request.user, urun=urunum)
                sepetim.adet += adet
                sepetim.toplam = urunum.fiyat * sepetim.adet
                sepetim.save()
                messages.success(request, 'Ürün Sepette Güncellendi')
                # return redirect('index')
            else:
                sepetim = Sepet.objects.create(
                    urun = urunum,
                    user = request.user,
                    adet = adet,
                    toplam = urunum.fiyat * adet
                )
                sepetim.save()
                messages.success(request, 'Ürün Sepete Eklendi')
                # return redirect('index')
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
        'toplam_urun_sayisi': toplam_urun_sayisi
    }


    return render(request, 'product-detail.html', context)

def aboutUs(request):
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


    if request.method == 'POST':
        urunId = request.POST['urunId']
        sepet = Sepet.objects.get(id=urunId)
        if 'guncelle' in request.POST:
            yeniAdet = request.POST['yeniAdet']

            if yeniAdet > '0':
                sepet.adet = yeniAdet
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

    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
        'sepetim': sepetim,
        'toplam_tutar': toplam_tutar,
        'toplam_urun_sayisi': toplam_urun_sayisi
    }
    return render(request, 'sepet.html', context)




