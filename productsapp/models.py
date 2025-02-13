from django.db import models
from purple.models import Category
from vendor.models import Vendors
from purple.models import *

# Create your models here.

class Products(models.Model):
    vendor = models.ForeignKey(Vendors,related_name='products', on_delete=models.CASCADE)
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
    product = models.ForeignKey(Products, related_name='product_images', on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to='products_images/')

    def __str__(self):
        return f"Image for {self.product.product_name}"

class BannerImage(models.Model):
    vendor = models.ForeignKey(Vendors,on_delete=models.CASCADE,related_name='food_banner')
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='food_banner_products')
    banner_image = models.ImageField(upload_to='banner_image',help_text='Upload the banner image')
    description = models.TextField(null=True,blank=True,help_text='Short description of the offer')
    is_active = models.BooleanField(default=True,help_text='only active banners will be displayed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.vendor.name}"

class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='wishlist')
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='wishlists')
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.product.product_name}'

class ProductReview(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)  # Allow null users
    rating = models.DecimalField(max_digits=2, decimal_places=1, help_text='Rating from 1 to 5')
    review = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username if self.user else "Anonymous"} - {self.product.product_name}'


class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='cart')
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='carts')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Set price when adding a product to the cart."""
        if not self.price:
            self.price = self.product.offerprice if self.product.offerprice else self.product.price
        super().save(*args, **kwargs)

    def total_price(self):
        '''
        calculate  total price using stored price
        '''

        return self.price * self.quantity

    def __str__(self):
        return f"Cart item for {self.user.username} - {self.product.product_name}"


class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    payment_method = models.CharField(
        max_length=100, choices=[('COD', 'Cash on Delivery'), ('Online', 'Online Payment')]
    )
    product_ids = models.CharField(max_length=255, null=True)
    product_names = models.CharField(max_length=255, null=True)
    total_price = models.FloatField(default=0.00)
    status = models.CharField(
        max_length=100, choices=[
            ('WAITING FOR CONFIRMATION', 'Waiting for confirmation'),
            ('CONFIRMED', 'Confirmed'),
            ('OUT FOR DELIVERY', 'Out for delivery'),
            ('DELIVERED', 'Delivered'),
            ('REJECTED', 'Rejected')
        ],
        default='WAITING FOR CONFIRMATION'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_ids = models.CharField(max_length=100, null=True, blank=True)
    total_cart_items = models.PositiveIntegerField(default=0)
    quantities = models.TextField(null=True, blank=True)
    delivery_pin = models.CharField(max_length=6, null=True, blank=True)

    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    pin_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Order by {self.user.email } - Payment: {self.payment_method}"
