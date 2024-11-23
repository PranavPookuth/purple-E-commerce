from random import randint

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, email, otp, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, otp=otp, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, otp=None, **extra_fields):
        # Automatically generate a random OTP if not provided
        if otp is None:
            otp = str(randint(100000, 999999))  # Random 6-digit OTP
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, otp, **extra_fields)



class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.username

    def is_otp_expired(self):
        """ Check if the OTP has expired (5 minutes window). """
        if not self.otp_generated_at:
            return True  # No OTP generated yet
        return timezone.now() > self.otp_generated_at + timezone.timedelta(minutes=5)


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    category_image = models.ImageField(upload_to='Images/',null=True,blank=True)
    def __str__(self):
        return self.category_name

class CarouselItem(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='carousel_images/')

    def __str__(self):
        return self.title

class BannerImage(models.Model):
    title = models.CharField(max_length=255,null=True,blank=True)
    banner_image = models.ImageField(upload_to='Banner_images/',null=True,blank=True)

class Products(models.Model):
    product_name = models.CharField(max_length=100)
    product_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    offerprice = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    isofferproduct = models.BooleanField()
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Discount Percentage")
    Popular_products = models.BooleanField()  # Correct name
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    newarrival = models.BooleanField()
    trending_one = models.BooleanField()

    def save(self, *args, **kwargs):
        """
        Override the save method to automatically calculate the offer price based on the discount and price.
        """
        if self.discount and self.price:
            discount_amount = (self.discount / 100) * self.price
            self.offerprice = self.price - discount_amount
        elif not self.discount:
            self.offerprice = self.price

        super(Products, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name

class ProductImage(models.Model):
    product = models.ForeignKey(Products,related_name='images',on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_image')

    def __str__(self):
        return f"Image for {self.product.product_name}"


