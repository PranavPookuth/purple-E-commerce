from random import randint
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


from random import randint
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, email, otp, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, email=email, otp=otp, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, otp=None, password=None, **extra_fields):
        if otp is None:
            otp = str(randint(100000, 999999))  # Random 6-digit OTP
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, otp, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # Required for admin access
    is_superuser = models.BooleanField(default=False)  # Required for superuser access
    is_active = models.BooleanField(default=True)  # Required for user activation
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.username

    def is_otp_expired(self):
        """Check if the OTP has expired (5-minute window)."""
        if not self.otp_generated_at:
            return True  # No OTP generated yet
        return timezone.now() > self.otp_generated_at + timezone.timedelta(minutes=5)

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='userprofile')
    contact_number = models.BigIntegerField(null=False,blank=False)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    whatsapp_number =models.BigIntegerField(null=False,blank=False)
    address = models.TextField(null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Profile of {self.user.username}"

    def get_email(self):
        """Return the email of the associated user."""
        return self.user.email


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
    Popular_products = models.BooleanField()
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


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart item for {self.user} - {self.product.name} "

    def total_price(self):
        return (self.product.offerprice or self.product.price) * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('WAITING FOR CONFIRMATION', 'Waiting for confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('OUT FOR DELIVERY', 'Out for delivery'),
        ('DELIVERED', 'Delivered'),
        ('REJECTED', 'Rejected')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100, choices=[('COD', 'Cash on Delivery'), ('Online', 'Online Payment')])
    product_ids = models.CharField(max_length=255, null=True)
    product_names = models.CharField(max_length=255, null=True)
    total_price = models.FloatField(default=0.00)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='WAITING FOR CONFIRMATION')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_ids = models.CharField(max_length=100, null=True, blank=True)
    total_cart_items = models.PositiveIntegerField(default=0)
    quantities = models.TextField(null=True, blank=True)  # Retaining quantities
    delivery_pin = models.CharField(max_length=6, null=True, blank=True)

    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    pin_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Order {self.unique_order_serial} by {self.user.email} - Payment: {self.payment_method}"

    def get_order_time(self):
        return self.created_at.strftime("Ordered on %Y-%m-%d at %I:%M%p")

