from django.contrib import admin
from django.utils.html import format_html
from .models import *
from django.utils.safestring import mark_safe


# Register your models here.
# class SepetAdmin(admin.ModelAdmin):
#     list_display = ('user', 'urun', 'adet', 'toplam', 'odendiMi')

class SepetAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_urun_image', 'urun', 'adet', 'toplam', 'odendiMi')

    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('get_first_name','get_last_name','get_email','get_country','get_city','get_district','get_address','get_phone','urun', 'adet', 'toplam', 'odendiMi'),
        }),
    )

    readonly_fields = ('get_first_name', 'get_last_name','get_email','get_phone','get_address','get_country','get_city','get_district')

    def get_first_name(self, obj):
        return obj.user.first_name
    
    def get_last_name(self, obj):
        return obj.user.last_name

    def get_email(self, obj):
        return obj.user.email
    
    def get_phone(self, obj):
        return obj.user.phone
    
    def get_address(self, obj):
        return obj.user.address
    
    def get_country(self, obj):
        return obj.user.country
    
    def get_city(self, obj):
        return obj.user.city
    
    def get_district(self, obj):
        return obj.user.district

    def get_urun_image(self, obj):
        return format_html('<img src="{}" width="75px" />', obj.urun.urunresmi.url)

    get_urun_image.short_description = 'Ürün Resmi'
    get_first_name.short_description = 'Adı'
    get_last_name.short_description = 'Soyadı'
    get_email.short_description = 'E-posta'
    get_phone.short_description = 'Telefon'
    get_address.short_description = 'Adres'
    get_country.short_description = 'Ülke'
    get_city.short_description = 'Şehir'
    get_district.short_description = 'İlçe'

class UrunAdmin(admin.ModelAdmin):
    list_display = ('kategori', 'isim', 'get_urun_image', 'fiyat', 'indirimli_fiyat', 'is_special')  # Gösterilecek sütunlar
    list_filter = ('kategori', 'is_special')  # Kategoriye göre filtreleme 
    list_editable = ('is_special',) 

    def get_urun_image(self, obj):
        return format_html('<img src="{}" width="75px" />', obj.urunresmi.url)

    get_urun_image.short_description = 'Ürün Resmi'

class SiparisUrunInline(admin.TabularInline):
    model = SiparisUrun
    extra = 0

class SiparisUrunAdmin(admin.ModelAdmin):
    list_display = ('siparis', 'urun', 'urun_stok_kodu', 'adet', 'birim_fiyat', 'urun_resmi_tag')

    
    def urun_resmi_tag(self, obj):
        if obj.urun_resmi:
            return format_html('<img src="{}" width="width="50" height="50" />', obj.urun_resmi.url)
        return "Resim Yok"
    urun_resmi_tag.short_description = 'Ürün Resmi'

class SiparisAdmin(admin.ModelAdmin):
    list_display = ('user', 'toplam_fiyat', 'satinalma_tarihi', 'odeme_bilgisi', 'siparis_iptal', 'kargoya_verildi', 'siparis_teslim_edildi')
    inlines = [SiparisUrunInline]

    # burası admin panelden değişiklik yapılmaması için/ değişiklik yapmak istenirse silinebilir
    readonly_fields = ( 
        'user',
        'toplam_fiyat',
        'teslimat_bilgileri_adi',
        'teslimat_bilgileri_soyadi',
        'teslimat_bilgileri_telefon',
        'teslimat_bilgileri_adres',
        'teslimat_bilgileri_ulke',
        'teslimat_bilgileri_sehir',
        'teslimat_bilgileri_ilce',
    )

    # def siparis_urun_resimleri(self, obj):
    #     siparis_urunler = obj.siparisurun_set.all()
    #     resimler = ''
    #     for urun in siparis_urunler:
    #         if urun.urun_resmi:
    #             resimler += f'<img src="{urun.urun_resmi.url}" width="50" height="50" />'
    #     return mark_safe(resimler)
    # siparis_urun_resimleri.allow_tags = True
    # siparis_urun_resimleri.short_description = 'Sipariş Ürün Resimleri'






admin.site.register(Slogan)
admin.site.register(Anakategori)
admin.site.register(Urun, UrunAdmin)
admin.site.register(Wrapperone)
admin.site.register(SocialMedia)
admin.site.register(Footer)
admin.site.register(Sepet, SepetAdmin)
admin.site.register(Hakkimizda)
admin.site.register(Uyelikmetni)
admin.site.register(Kvkkmetni)
admin.site.register(Mesafelisatisozlesmesi)
admin.site.register(Gizliliksozlesmesi)
admin.site.register(Iptalveiade)
admin.site.register(Kurulum)
admin.site.register(SiparisUrun, SiparisUrunAdmin)
admin.site.register(Siparis, SiparisAdmin)

