from django.contrib import admin
from django.utils.html import format_html
from .models import *



# Register your models here.
# class SepetAdmin(admin.ModelAdmin):
#     list_display = ('user', 'urun', 'adet', 'toplam', 'odendiMi')

class SepetAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_urun_image', 'urun', 'adet', 'toplam', 'odendiMi')

    def get_urun_image(self, obj):
        return format_html('<img src="{}" width="75px" />', obj.urun.urunresmi.url)

    get_urun_image.short_description = 'Ürün Resmi'

class UrunAdmin(admin.ModelAdmin):
    list_display = ('kategori', 'isim', 'get_urun_image', 'fiyat', 'indirimli_fiyat', 'is_special')  # Gösterilecek sütunlar
    list_filter = ('kategori',)  # Kategoriye göre filtreleme 

    def get_urun_image(self, obj):
        return format_html('<img src="{}" width="75px" />', obj.urunresmi.url)

    get_urun_image.short_description = 'Ürün Resmi'


admin.site.register(Slogan)
admin.site.register(Anakategori)
admin.site.register(Urun, UrunAdmin)
admin.site.register(Wrapperone)
admin.site.register(SocialMedia)
admin.site.register(Footer)
admin.site.register(Sepet, SepetAdmin)

