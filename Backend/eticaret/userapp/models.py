from django.contrib.auth.models import AbstractUser
from django.db import models



class MyUser(AbstractUser):
    # Ekstra alanları burada tanımlayın
    phone = models.CharField(max_length=11, blank=True, null=True)
    address = models.TextField(max_length=250, blank=True, null=True, default='')
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True, default='')
