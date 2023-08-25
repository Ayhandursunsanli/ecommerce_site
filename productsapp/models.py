from django.db import models
from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField
from userapp.forms import UserProfileForm



# Create your models here.


User = get_user_model()

class Slogan(models.Model):
    gorsel = models.ImageField(upload_to='headerphoto/', blank=False, null=False)
    miniBaslik = models.CharField(max_length=100)
    buyukBaslik = models.CharField(max_length=100)
    aciklama = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Ana Sayfa Header'

    def __str__(self):
        return self.buyukBaslik

class Anakategori(models.Model):
    anakategoriGorsel = models.ImageField(upload_to='anakategoriphoto/', blank=False, null=False)
    anakategoriBaslik = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Anakategoriler'

    def __str__(self):
        return self.anakategoriBaslik

class Wrapperone(models.Model):
    wrapperResim1 = models.ImageField(upload_to='wrapperphoto/', blank=False, null=False)
    wrapperResim2 = models.ImageField(upload_to='wrapperphoto/', blank=True, null=True)
    wrapperResim3 = models.ImageField(upload_to='wrapperphoto/', blank=True, null=True)
    wrapperResim4 = models.ImageField(upload_to='wrapperphoto/', blank=True, null=True)
    wrapperResim5 = models.ImageField(upload_to='wrapperphoto/', blank=True, null=True)
    wrapperText = models.CharField(max_length=200, blank=True, null= True)

    class Meta:
        verbose_name_plural = 'Banner(Afiş)' 
    def __str__(self):
        return self.wrapperText

class Urun(models.Model):
    urunresmi = models.ImageField(upload_to='urunphoto/', blank=False, null=False, default='', verbose_name='1. Ürün Resmi (Zorunlu)')
    urunresmiTwo = models.ImageField(upload_to='urunphoto/', blank=True, null=False, default='', verbose_name='2. Ürün Resmi')
    urunresmiThree = models.ImageField(upload_to='urunphoto/', blank=True, null=False, default='', verbose_name='3. Ürün Resmi')
    urunresmiFour = models.ImageField(upload_to='urunphoto/', blank=True, null=False, default='',verbose_name='4. Ürün Resmi')
    kategori = models.CharField(max_length=100, blank=False, default='')
    stokKodu = models.CharField(max_length=100, blank=False, default='', verbose_name='Stok Kodu')
    urunRengi = models.CharField(max_length=100, blank=False, default='', verbose_name='Şapka Rengi veya Deseni')
    ayakKaplama = models.CharField(max_length=100, blank=False, null=True, verbose_name='Ayak Kaplama Rengi')
    isim = models.CharField(max_length= 100, verbose_name='Model İsmi')
    aciklama = models.TextField(max_length=500, verbose_name='Açıklama')
    teknikDetaylar = RichTextField(blank=True, null=True, verbose_name='Teknik Detaylar')
    fiyat = models.DecimalField(max_digits=8, decimal_places=2)
    indirimli_fiyat = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='İndirimli Fiyat')
    is_special = models.BooleanField(default=False, verbose_name='Ana Sayfada Göster')

    class Meta:
        verbose_name_plural = 'Ürünler' 
    def __str__(self):
        return self.isim

class SocialMedia(models.Model):
    name = models.CharField(max_length=50, blank=True, null= True)
    photo = models.ImageField(upload_to='footersocialmedia_photos/')
    link = models.URLField(max_length=1000)

    class Meta:
        verbose_name_plural = 'Sosyal Medyalar' 

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
    toplam = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    # toplam = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    odendiMi = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Sepetler'

    def __str__(self):
        return self.user.username
    
    
    def hesapla_toplam(self):
        fiyat = self.urun.fiyat
        if self.urun.indirimli_fiyat:
            fiyat = self.urun.indirimli_fiyat
        return self.adet * fiyat

class Hakkimizda(models.Model):
    vizyonResim = models.ImageField(upload_to='hakkimzda/', blank=False, null=False, verbose_name='Vizyon Resim')
    vizyon = RichTextField(blank=True, null=True, verbose_name='Vizyonumuz')
    misyonResim = models.ImageField(upload_to='hakkimzda/', blank=False, null=False, verbose_name='Misyon Resim')
    misyon = RichTextField(blank=True, null=True, verbose_name='Misyonumuz')
    degerlerimizResim = models.ImageField(upload_to='hakkimzda/', blank=False, null=False, verbose_name='Değerlerimiz Resim')
    degerlerimiz = RichTextField(blank=True, null=True, verbose_name='Degerlerimiz')

    class Meta:
        verbose_name_plural = 'Hakkımızda'

class Uyelikmetni(models.Model):
    uyelikBaslik = models.CharField(max_length=100, blank=False, null=True, verbose_name='Üyelik Metni Başlığı')
    uyelikmetni = RichTextField(blank=True, null=True, verbose_name='Üyelik Metni')

    class Meta:
        verbose_name_plural = 'Üyelik Metni'

class Kvkkmetni(models.Model):
    kvkkBaslik = models.CharField(max_length=100, blank=False, null=True, verbose_name='KVKK Metni Başlığı')
    kvkkmetni = RichTextField(blank=True, null=True, verbose_name='KVKK Metni')

    class Meta:
        verbose_name_plural = 'KVKK Metni'

class Mesafelisatisozlesmesi(models.Model):
    mesafeliBaslik = models.CharField(max_length=150, blank=False, null=True, verbose_name='Mesafeli Satış Sözleşmesi Başlığı')
    mesafelimetni = RichTextField(blank=True, null=True, verbose_name='Mesafeli Satış Sözleşmesi Metni')

    class Meta:
        verbose_name_plural = 'Mesafeli Satış Sözleşmesi'

class Gizliliksozlesmesi(models.Model):
    gizlilikBaslik = models.CharField(max_length=150, blank=False, null=True, verbose_name='Gizlilik ve Güvenlik Başlığı')
    gizlilikmetni = RichTextField(blank=True, null=True, verbose_name='Gizlilik ve Güvenlik Metni')

    class Meta:
        verbose_name_plural = 'Gizlilik ve Güvenlik Sözleşmesi'

class Iptalveiade(models.Model):
    iptalveiadeBaslik = models.CharField(max_length=150, blank=False, null=True, verbose_name='İptal ve İade Koşulları Metni Başlığı')
    iptalveiademetni = RichTextField(blank=True, null=True, verbose_name='İptal ve İade Koşulları Metni')

    class Meta:
        verbose_name_plural = 'İptal ve İade Koşulları Metni'

class Kurulum(models.Model):
    video_url = models.URLField(blank=False, null=True,)
    kurulumAciklamasi = RichTextField(blank=True, null=True, verbose_name='Kurulum Açıklaması')

    class Meta:
        verbose_name_plural = 'Kurulum Bilgilendirme'

class Siparis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Kullanıcı Adı')
    urunler = models.ManyToManyField(Urun, through='SiparisUrun', verbose_name='Satın Alınan Ürünler')
    toplam_fiyat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Toplam Fiyat')
    satinalma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name='Satın Alma Tarihi')
    odeme_bilgisi = models.BooleanField(default=False, verbose_name='Ödeme Bilgisi')
    kargoya_verildi = models.BooleanField(default=False, verbose_name='Kargoya Verildi')
    siparis_teslim_edildi = models.BooleanField(default=False, verbose_name='Sipariş Teslim Edildi')
    siparis_iptal = models.BooleanField(default=False, verbose_name='Sipariş İptal')
    teslimat_bilgileri_adi = models.CharField(max_length=200, blank=False, null=True, verbose_name='Adı')
    teslimat_bilgileri_soyadi = models.CharField(max_length=200, blank=False, null=True, verbose_name='Soyadı')
    teslimat_bilgileri_telefon = models.CharField(max_length=200, blank=False, null=True, verbose_name='Telefon')
    teslimat_bilgileri_email = models.EmailField(max_length=200, blank=False, null=True, verbose_name='E-Mail')
    teslimat_bilgileri_adres = models.TextField(max_length=200, blank=False, null=True, verbose_name='Adress')
    teslimat_bilgileri_ulke = models.CharField(max_length=200, blank=False, null=True, verbose_name='Ülke')
    teslimat_bilgileri_sehir = models.CharField(max_length=200, blank=False, null=True, verbose_name='Şehir')
    teslimat_bilgileri_ilce = models.CharField(max_length=200, blank=False, null=True, verbose_name='İlçe')



    class Meta:
        verbose_name_plural = 'Siparişler'

    def __str__(self):
        return f"Sipariş - {self.user.username}"

class SiparisUrun(models.Model):
    siparis = models.ForeignKey(Siparis, on_delete=models.CASCADE)
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE)
    urun_stok_kodu = models.CharField(max_length=50, null=True, verbose_name='Ürün Stok Kodu')
    adet = models.PositiveIntegerField(default=1, verbose_name='Adet')
    birim_fiyat = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Birim Fiyat')
    urun_resmi = models.ImageField(upload_to='siparis_urun_resimleri/', blank=True, null=True, verbose_name='Ürün Resmi')

    class Meta:
        verbose_name_plural = 'Sipariş Ürünleri'
    
    def toplam_fiyat(self):
        return self.adet * self.birim_fiyat