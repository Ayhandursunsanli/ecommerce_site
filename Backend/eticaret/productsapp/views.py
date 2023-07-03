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
    context = {
        'slogan': slogan,
        'anakategori' : anakategori,
        'urunler' : urunler,
        'wrapperone' : wrapperOne,
        'footer' : footer,
        'social_media' : socail_media,
    }
    return render(request, 'index.html', context)

# def register(request):
#     anakategori = Anakategori.objects.all()
#     context = {
#         'anakategori' : anakategori,
#     }
#     return render(request, 'register.html', context)

# def login(request):
#     anakategori = Anakategori.objects.all()
#     context = {
#         'anakategori' : anakategori,
#     }
#     return render(request, 'login.html', context)

# def allProduct(request):
#     urunler = Urun.objects.all()
#     anakategori = Anakategori.objects.all()
#     context = {
#         'anakategori' : anakategori,
#         'urunler' : urunler,
#     }

#     return render(request, 'all-product.html', context)



def allProduct(request):
    urunler = Urun.objects.all()
    anakategori = Anakategori.objects.all()
    wrapperOne = Wrapperone.objects.all()
    sort_option = request.GET.get('sort_option')
    search_query = request.GET.get('search_query')
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()

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
                return redirect('index')
            else:
                sepetim = Sepet.objects.create(
                    urun = urunum,
                    user = request.user,
                    adet = adet,
                    toplam = urunum.fiyat * adet
                )
                sepetim.save()
                messages.success(request, 'Ürün Sepete Eklendi')
                return redirect('index')
        else:
            messages.error(request, 'Giriş Yapmanız Gerekiyor')
            return redirect('login')
    context = {
        'anakategori' : anakategori,
        'urun' : urunum,
        'wrapperone' : wrapperOne,
        'ayniKategoridekiUrunler' : ayniKategoridekiUrunler,
        'footer' : footer,
        'social_media' : socail_media,
    }
    return render(request, 'product-detail.html', context)


def aboutUs(request):
    anakategori = Anakategori.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
    }
    return render(request, 'about-us.html', context)

def contactUs(request):
    anakategori = Anakategori.objects.all()
    socail_media = SocialMedia.objects.all()
    footer = Footer.objects.first()
    context = {
        'anakategori' : anakategori,
        'footer' : footer,
        'social_media' : socail_media,
    }
    return render(request, 'contact-us.html', context)


# def sepet(request):
#     user = request.user
#     sepetim = Sepet.objects.filter(user = user)
#     if request.method == 'POST':
#         urunId = request.POST['urunId']
#         silinen = Sepet.objects.get(id = urunId)
#         silinen.delete()
#         messages.success(request, 'Ürün sepetten kaldırıldı.')
#         return redirect('sepet')
#     context= {
#         'sepetim' : sepetim
#     }
#     return render(request, 'sepet.html', context)




def sepet(request):
    user = request.user
    sepetim = Sepet.objects.filter(user=user)
    toplam_tutar = Decimal('0.00')

    if request.method == 'POST':
        urunId = request.POST['urunId']
        silinen = Sepet.objects.get(id=urunId)
        toplam_tutar -= silinen.toplam  # Çıkarılan ürünün toplam fiyatını toplam tutardan çıkar
        silinen.delete()
        messages.success(request, 'Ürün sepetten kaldırıldı.')
        return redirect('sepet')

    for sepet in sepetim:
        toplam_tutar += sepet.hesapla_toplam()
    
    

    context = {
        'sepetim': sepetim,
        'toplam_tutar': toplam_tutar
    }
    return render(request, 'sepet.html', context)




