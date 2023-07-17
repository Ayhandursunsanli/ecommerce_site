from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
from decimal import Decimal
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.db.models import Count



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
    urunler = Urun.objects.filter(kategori=categoryName)
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
    kdv = int(toplam_tutar * Decimal('0.2'))
    araToplam = int(toplam_tutar - Decimal(kdv))



    if request.method == 'POST':
        urunId = request.POST['urunId']
        sepet = Sepet.objects.get(id=urunId)
        if 'guncelle' in request.POST:
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

def hesabim(request):
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
    return render(request, 'hesabim.html', context)

def loading_page(request):
    return render(request, 'includes/_loading.html')


