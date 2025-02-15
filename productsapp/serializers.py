import random
import uuid
import pytz
from django.conf import settings
from rest_framework import serializers
from  .models import *
from vendor.models import Vendors
from purple.models import *


class ProductImageSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'product_image']

    def get_product_image(self, obj):
        request = self.context.get('request')
        if obj.product_image:
            return request.build_absolute_uri(obj.product_image.url) if request else f"{settings.MEDIA_URL}{obj.product_image.url}"
        return None



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


class BannerImageSerializer(serializers.ModelSerializer):
    banner_image = serializers.ImageField(required=True)
    is_active = serializers.BooleanField(default=True)
    class Meta:
        model = BannerImage
        fields = ['id', 'vendor', 'product', 'banner_image', 'description', 'is_active', 'created_at', 'updated_at']

    def get_banner_image(self, obj):
        request = self.context.get('request')
        if obj.banner_image:
            return request.build_absolute_uri(obj.banner_image.url) if request else obj.banner_image.url
        return None



class WishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    price = serializers.DecimalField(source='product.offerprice', max_digits=10, decimal_places=2, read_only=True)
    description = serializers.CharField(source='product.product_description', read_only=True)
    image = serializers.SerializerMethodField()  # To get the image URL

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'added', 'product_name', 'price', 'description', 'image']
        read_only_fields = ['id', 'added']

    def get_image(self, obj):
        # Get the first image associated with the product
        product_images = obj.product.product_images.all()
        if product_images.exists():
            image_path = product_images.first().product_image.url
            # Get the full URL by combining the domain with the relative path
            full_url = obj.product.product_images.first().product_image.url
            # Using build_absolute_uri to get the full absolute URL
            return settings.SITE_URL + full_url  # Assuming you have SITE_URL set in settings.py
        return None

class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'product_name', 'user', 'rating', 'review', 'created_at']
        read_only_fields = ['id', 'created_at', 'user', 'product_name']

class CartSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)  # You must define get_user()
    product = ProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "product", "quantity", "price", "total_price", "created_at", "updated_at"]
        read_only_fields = ["id", "total_price", "created_at", "updated_at"]

    def get_user(self, obj):
        """Return the user's username or ID."""
        return obj.user.username  # Or `obj.user.id` if you prefer the ID

    def get_total_price(self, obj):
        """Calculate total price dynamically."""
        price = obj.product.offerprice if obj.product.isofferproduct and obj.product.offerprice else obj.product.price
        return price * obj.quantity if price else 0  # Fallback to 0 if price is None



class CheckoutSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(write_only=True, required=False)  # Accept user_name from request

    class Meta:
        model = Order
        fields = [
            "id", "user_name", "payment_method", "product_ids", "product_names", "quantities",
            "total_price", "total_cart_items", "address", "city", "state",
            "pin_code", "status", "order_ids"
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        user_name = validated_data.pop("user_name", None)  # Remove user_name before saving

        # Fetch cart items for the user
        cart_items = Cart.objects.filter(user=user) if user else Cart.objects.all()
        if not cart_items.exists():
            raise serializers.ValidationError(["Your cart is empty."])

        product_ids = [str(item.product.id) for item in cart_items]
        product_names = [item.product.product_name for item in cart_items]
        quantities = [str(item.quantity) for item in cart_items]
        total_price = sum(item.total_price() for item in cart_items)
        total_cart_items = cart_items.count()

        unique_order_id = str(uuid.uuid4())[:8]  # Generate unique order ID

        # Create Order
        order = Order.objects.create(
            user=user,
            payment_method=validated_data.get("payment_method"),
            product_ids=",".join(product_ids),
            product_names=",".join(product_names),
            quantities=",".join(quantities),
            total_price=total_price,
            total_cart_items=total_cart_items,
            address=validated_data.get("address"),
            city=validated_data.get("city"),
            state=validated_data.get("state"),
            pin_code=validated_data.get("pin_code"),
            status="WAITING FOR CONFIRMATION",
            order_ids=unique_order_id
        )
        cart_items.delete()
        return order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id", "payment_method", "product_ids", "product_names", "quantities",
            "total_price", "total_cart_items", "address", "city", "state",
            "pin_code", "status", "order_ids", "delivery_pin", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "order_ids", "delivery_pin", "created_at", "updated_at"]

    def create(self, validated_data):
        # Fetch all cart items (without authentication)
        cart_items = Cart.objects.all()
        if not cart_items.exists():
            raise serializers.ValidationError({"cart": "Your cart is empty."})

        # Extract product details
        product_ids = [str(item.product.id) for item in cart_items]
        product_names = [item.product.product_name for item in cart_items]
        quantities = [str(item.quantity) for item in cart_items]
        total_price = sum(item.total_price() for item in cart_items)
        total_cart_items = cart_items.count()

        # Generate unique order ID and delivery PIN
        validated_data["order_ids"] = str(uuid.uuid4())[:8]
        validated_data["delivery_pin"] = str(random.randint(100000, 999999))

        # Assign cart data
        validated_data["product_ids"] = ",".join(product_ids)
        validated_data["product_names"] = ",".join(product_names)
        validated_data["quantities"] = ",".join(quantities)
        validated_data["total_price"] = total_price
        validated_data["total_cart_items"] = total_cart_items

        # Create the order
        order = super().create(validated_data)


        return order