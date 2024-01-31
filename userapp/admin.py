from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser

class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'country', 'city', 'district')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')

admin.site.register(MyUser, MyUserAdmin)

