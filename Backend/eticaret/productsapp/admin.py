from django.contrib import admin
from .models import *
# from .models import Slogan
# from .models import Anakategori
# from .models import Urun (yıldızla hepsini çektim uğraşmamak için)


# Register your models here.


admin.site.register(Slogan)
admin.site.register(Anakategori)
admin.site.register(Urun)
admin.site.register(Wrapperone)
admin.site.register(SocialMedia)
admin.site.register(Footer)
