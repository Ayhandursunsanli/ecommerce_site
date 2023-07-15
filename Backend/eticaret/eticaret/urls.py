"""eticaret URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from productsapp.views import *
from django.conf.urls.static import static
from django.conf import settings
from userapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),

    path('user/', include('userapp.urls')),

    path('allProduct/',allProduct,name='allProduct'),
    path('category/<str:categoryName>',category,name='category'),
    path('product/<int:urunId>', productDetail, name='product'),
    path('about-us/', aboutUs, name='about-us'),
    path('contact-us/', contactUs, name='contact-us'),
    path('sepet/', sepet, name='sepet'),
    path('loading/', loading_page, name='loading'),
    # path('hesabim/', hesabim, name='hesabim'), #userapp içindeki url yazılıp buraya çekilecek
    # path('teslimat/', teslimat, name='teslimat'), #userapp içindeki url yazılıp buraya çekilecek
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)