from random import randint
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, email, otp=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)  # Ensure user is active

        user = self.model(username=username, email=email, otp=otp, **extra_fields)
        user.set_password(extra_fields.get("password", None))  # Ensure password is set correctly
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, otp=None, **extra_fields):
        if otp is None:
            otp = str(random.randint(100000, 999999))  # Generate a random OTP

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, otp, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):  # Added PermissionsMixin
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)  # Required for superuser creation
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.username

    def is_otp_expired(self):
        """ Check if the OTP has expired (5 minutes window). """
        if not self.otp_generated_at:
            return True  # No OTP generated yet
        expiration_time = self.otp_generated_at + timezone.timedelta(minutes=5)
        return timezone.now() > expiration_time



class Address(models.Model):
    user = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}, {self.country}, {self.pincode}"

    class Meta:
        ordering = ['-created_at']

class Category(models.Model):
    category_name =  models.CharField(max_length=100,null=False,blank=False)
    category_image = models.ImageField(upload_to='category_image')
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.category_name

class Carousel(models.Model):
    title = models.CharField(max_length=100)
    carousel_image = models.ImageField(upload_to='Carousel_images',null=False,blank=False)




