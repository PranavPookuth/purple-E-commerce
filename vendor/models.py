from django.db import models
from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from rest_framework.permissions import BasePermission
import random
import uuid

# Create your models here.
class Vendors(models.Model):
    name = models.CharField(max_length=225,unique=True)
    contact_number = models.CharField(max_length=15,unique=True)
    whatsapp_number = models.CharField(max_length=15,unique=True)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    display_image = models.ImageField(upload_to='display_image', null=False, blank=False)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

    @property
    def is_fully_active(self):
        """Determine if the vendor is active and approved."""
        return self.is_active and self.is_approved

    def generate_otp(self):
        """Generate a random 6-digit OTP and set expiry."""
        self.otp = str(random.randint(100000, 999999))
        self.otp_expiry = datetime.now() + timedelta(minutes=5)
        self.save()
