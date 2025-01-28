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


