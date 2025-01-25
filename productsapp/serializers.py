from rest_framework import serializers
from  .models import *
from vendor.models import Vendors


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id','product_image']