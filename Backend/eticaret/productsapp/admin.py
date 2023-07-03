from django.contrib import admin
from .models import *



# Register your models here.
class SepetAdmin(admin.ModelAdmin):
    list_display = ('user', 'urun', 'adet', 'toplam', 'odendiMi')

admin.site.register(Slogan)
admin.site.register(Anakategori)
admin.site.register(Urun)
admin.site.register(Wrapperone)
admin.site.register(SocialMedia)
admin.site.register(Footer)
admin.site.register(Sepet, SepetAdmin)
