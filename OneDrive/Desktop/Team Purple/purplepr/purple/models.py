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

    def create_superuser(self, username, email, otp, **extra_fields):
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


class BannerImage(models.Model):
    banner_title = models.CharField(max_length=100,null=True,blank=True)
    banner_image = models.ImageField(upload_to='banner/',null=True,blank=True)

    def __str__(self):
        return self.banner_title

class CaruoselItem(models.Model):
    title = models.CharField(max_length=100,null=True,blank=True)
    carusoel_image = models.ImageField(upload_to='carousel_images/')

    def __str__(self):
        return self.title

class Products(models.Model):
    product_name = models.CharField(max_length=100)
    product_description = models.TextField()
    product_price = models.DecimalField(max_digits=10,decimal_places=2)
    offer_price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    product_image = models.ImageField(upload_to='products_image/',null=True,blank=True)
    category = models.ForeignKey(Category,related_name='products',on_delete=models.CASCADE)
    isofferproduct = models.BooleanField(default=False)
    ispopular = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.product_name

