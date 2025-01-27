from rest_framework import serializers
from  .models import *
from vendor.models import Vendors


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'product_image']

    def get_images(self, obj):
        request = self.context.get('request')
        images = ProductImage.objects.filter(product=obj)
        return [
            request.build_absolute_uri(image.product_image.url) if request else image.product_image.url
            for image in images
        ]


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = [
            'id', 'product_name', 'product_description', 'price', 'offerprice',
            'isofferproduct', 'discount', 'Popular_products', 'created_at',
            'newarrival', 'trending_one', 'vendor', 'category', 'images'
        ]

    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.product_images.all()  # Access related ProductImage objects
        return [
            request.build_absolute_uri(image.product_image.url) if request else image.product_image.url
            for image in images
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    image_urls = ProductImageSerializer(source='product_images', many=True, read_only=True)

    class Meta:
        model = Products
        fields = ['id', 'vendor', 'vendor_name', 'category', 'category_name', 'product_name', 'product_description',
                  'price', 'offerprice', 'discount', 'isofferproduct', 'Popular_products', 'newarrival', 'trending_one',
                  'images', 'image_urls', 'created_at']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Products.objects.create(**validated_data)
        for image_data in images_data:
            ProductImage.objects.create(product=product, product_image=image_data)
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])

        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle image uploads (replace old images if necessary)
        if images_data:
            instance.product_images.all().delete()  # Delete old images before adding new ones
            for image_data in images_data:
                ProductImage.objects.create(product=instance, product_image=image_data)

        return instance

class ProductListSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    image_urls = ProductImageSerializer(source='product_images', many=True, read_only=True)

    class Meta:
        model = Products
        fields = [
            'id', 'vendor', 'vendor_name', 'category', 'category_name',
            'product_name', 'product_description', 'price', 'offerprice',
            'discount', 'isofferproduct', 'Popular_products', 'newarrival',
            'trending_one', 'image_urls', 'isofferproduct'
        ]

class ProductSearchSerializer(serializers.Serializer):
    search_query = serializers.CharField(required=True)
