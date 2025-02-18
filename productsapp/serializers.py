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
            "pin_code", "status", "order_ids", "delivery_pin"  # Ensure delivery_pin is included
        ]

    def create(self, validated_data):
        request = self.context.get('request')

        # Check if the user_name is provided in the request
        user_name = validated_data.pop("user_name", None)

        if not user_name:
            raise serializers.ValidationError("User name is required.")

        try:
            user = User.objects.get(username=user_name)  # Retrieve user by username
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        # Fetch cart items for the user
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            raise serializers.ValidationError(["Your cart is empty."])

        product_ids = [str(item.product.id) for item in cart_items]
        product_names = [item.product.product_name for item in cart_items]
        quantities = [str(item.quantity) for item in cart_items]
        total_price = sum(item.total_price() for item in cart_items)
        total_cart_items = cart_items.count()

        unique_order_id = str(uuid.uuid4())[:8]  # Generate unique order ID

        # Create the order, ensuring delivery_pin is stored
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
            delivery_pin=validated_data.get("pin_code"),  # Store pin_code in delivery_pin
            status="CONFIRMED ",
            order_ids=unique_order_id
        )

        # Clear the user's cart after checkout
        cart_items.delete()

        return order




class OrderSerializer(serializers.ModelSerializer):
    # Use the 'username' field from the related User object.
    user_name = serializers.CharField(source='user.username', read_only=True)
    order_time = serializers.SerializerMethodField()
    cart_products = CartSerializer(source='cart.products', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_name', 'status', 'created_at', 'product_names', 'payment_method', 'product_ids',
                  'total_price', 'order_ids', 'cart_products', 'total_cart_items', 'order_time']

    def get_order_time(self, obj):
        # Convert to IST (Indian Standard Time)
        ist_timezone = pytz.timezone('Asia/Kolkata')
        created_at_ist = obj.created_at.astimezone(ist_timezone)

        # Format the datetime in the desired format
        return created_at_ist.strftime("%d/%m/%Y at %I:%M%p")

class OrderDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    Address = serializers.CharField(source='user.address', read_only=True)
    total_price = serializers.ReadOnlyField()
    cart_products = serializers.SerializerMethodField()
    order_time = serializers.SerializerMethodField()
    delivery_pin = serializers.CharField(read_only=True)  # Ensure it's included

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_name', 'status', 'created_at',
            'product_names', 'payment_method', 'product_ids',
            'total_price', 'order_ids', 'cart_products', 'Address',
            'total_cart_items', 'order_time', 'delivery_pin'  # Ensure it's in response
        ]

    def get_order_time(self, obj):
        return obj.created_at.strftime("%d/%m/%Y at %I:%M%p")

    def get_cart_products(self, obj):
        product_ids = obj.product_ids.split(",") if obj.product_ids else []
        product_names = obj.product_names.split(",") if obj.product_names else []
        quantities = obj.quantities.split(",") if obj.quantities else []

        products = Products.objects.filter(id__in=product_ids)

        cart_products = []
        for product in products:
            index = product_ids.index(str(product.id))
            quantity = int(quantities[index]) if len(quantities) > index else 1

            cart_products.append({
                "name": product_names[index],
                "quantity": quantity,
                "price": str(product.price)
            })

        return cart_products


class AllOrdersSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    cart_products = CartSerializer(source='cart.products', many=True, read_only=True)
    order_time = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_name', 'status', 'payment_method', 'order_ids',
                  'delivery_pin', 'cart_products', 'order_time']

    def get_order_time(self, obj):
        # Convert to IST (Indian Standard Time)
        ist_timezone = pytz.timezone('Asia/Kolkata')
        created_at_ist = obj.created_at.astimezone(ist_timezone)

        # Format the datetime in the desired format
        return created_at_ist.strftime("%d/%m/%Y at %I:%M%p")

class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        ('WAITING FOR CONFIRMATION', 'Waiting for confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('OUT FOR DELIVERY', 'Out for delivery'),
        ('DELIVERED', 'Delivered'),
        ('REJECTED','rejected')
    ])