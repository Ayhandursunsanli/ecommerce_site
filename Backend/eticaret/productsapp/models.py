from django.db import models


# Create your models here.




class Slogan(models.Model):
    gorsel = models.ImageField(upload_to='headerphoto/', blank=False, null=False)
    miniBaslik = models.CharField(max_length=100)
    buyukBaslik = models.CharField(max_length=100)
    aciklama = models.CharField(max_length=100)

class Anakategori(models.Model):
    anakategoriGorsel = models.ImageField(upload_to='headerphoto/', blank=False, null=False)
    anakategoriBaslik = models.CharField(max_length=50)

class Urun(models.Model):
    urunresmi = models.ImageField(upload_to='urunphoto/', blank=False, null=False, default='')
    kategori = models.CharField(max_length=100, blank=False, default='')
    isim = models.CharField(max_length= 100)
    aciklama = models.TextField(max_length=500)
    fiyat = models.DecimalField(max_digits=8, decimal_places=2)

    # __str__ : admin panelinde göstermek istediğimiz bilgi.
    def __str__(self):
        return self.isim
