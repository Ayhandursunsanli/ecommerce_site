from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_request, name='login'),
    path('logout/',logout_request,name='logout'),
    path('update_profile/', update_profile, name='update_profile'),
    path('new_password/', new_password, name='new_password'),
    path('teslimat/', teslimat, name='teslimat'),
    path('activate/<str:uidb64>/<str:token>/', activate, name='activate'),
]
