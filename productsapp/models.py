from django.db import models
from purple.models import Category
from vendor.models import Vendors

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
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='images')
    product_image = models.ImageField(upload_to='Product_Image',null=False,blank=True)

    def __str__(self):
        return f"Image for {self.product.product_name}"



