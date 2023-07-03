from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.


User = get_user_model()

class Slogan(models.Model):
    gorsel = models.ImageField(upload_to='headerphoto/', blank=False, null=False)
    miniBaslik = models.CharField(max_length=100)
    buyukBaslik = models.CharField(max_length=100)
    aciklama = models.CharField(max_length=100)

class Anakategori(models.Model):
    anakategoriGorsel = models.ImageField(upload_to='headerphoto/', blank=False, null=False)
    anakategoriBaslik = models.CharField(max_length=50)

class Wrapperone(models.Model):
    wrapperResim1 = models.ImageField(upload_to='wrapperphoto/', blank=False, null=False)
    wrapperResim2 = models.ImageField(upload_to='wrapperphoto/', blank=True, null=True)
    wrapperResim3 = models.ImageField(upload_to='wrapperphoto/', blank=True, null=True)
    wrapperResim4 = models.ImageField(upload_to='wrapperphoto/', blank=True, null=True)
    wrapperResim5 = models.ImageField(upload_to='wrapperphoto/', blank=True, null=True)
    wrapperText = models.CharField(max_length=200, blank=True, null= True)


class Urun(models.Model):
    urunresmi = models.ImageField(upload_to='urunphoto/', blank=False, null=False, default='')
    urunresmiTwo = models.ImageField(upload_to='urunphoto/', blank=True, null=False, default='')
    urunresmiThree = models.ImageField(upload_to='urunphoto/', blank=True, null=False, default='')
    urunresmiFour = models.ImageField(upload_to='urunphoto/', blank=True, null=False, default='')
    kategori = models.CharField(max_length=100, blank=False, default='')
    stokKodu = models.CharField(max_length=100, blank=False, default='')
    urunRengi = models.CharField(max_length=100, blank=False, default='')
    isim = models.CharField(max_length= 100)
    aciklama = models.TextField(max_length=500)
    fiyat = models.DecimalField(max_digits=8, decimal_places=2)
    indirimli_fiyat = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    is_special = models.BooleanField(default=False)

    # __str__ : admin panelinde göstermek istediğimiz bilgi.
    def __str__(self):
        return self.isim

class SocialMedia(models.Model):
    name = models.CharField(max_length=50, blank=True, null= True)
    photo = models.ImageField(upload_to='footersocialmedia_photos/')
    link = models.URLField(max_length=1000)

    def __str__(self):
        return self.name


class Footer(models.Model):
    site_description = models.CharField(max_length=200)
    company_address = models.CharField(max_length=200)
    company_phone = models.CharField(max_length=15)
    company_email = models.CharField(max_length=50, blank=False, null=True)
    whatsapp_number = models.CharField(max_length=15,)
    social_media = models.ManyToManyField(SocialMedia, blank=True)
    

    def __str__(self):
        return self.site_description



class Sepet(models.Model):
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    adet = models.IntegerField(default=1)
    toplam = models.IntegerField(null=True)
    # toplam = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    odendiMi = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
    def hesapla_toplam(self):
        return self.adet * self.urun.fiyat
    