from django.contrib.auth.models import AbstractUser
from django.db import models

class MyUser(AbstractUser):
    # Ekstra alanları burada tanımlayın
    phone = models.CharField(max_length=11, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)