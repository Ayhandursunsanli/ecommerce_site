from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_request, name='login'),
    path('logout/',logout_request,name='logout'),
]
