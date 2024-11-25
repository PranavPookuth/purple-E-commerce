from rest_framework import serializers
from .models import *
from django.core.mail import send_mail
import random
import uuid
from django.utils import timezone

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

    def validate_email(self, value):
        """
        Check if the email is already registered and verified.
        """
        try:
            user = User.objects.get(email=value)
            if user.is_verified:
                raise serializers.ValidationError("User with this email is already verified.")
            else:
                # Allow OTP regeneration for unverified users
                self.context['existing_user'] = user
        except User.DoesNotExist:
            pass
        return value

    def create(self, validated_data):
        if 'existing_user' in self.context:
            # User exists but is not verified, regenerate OTP
            user = self.context['existing_user']
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            # Resend OTP via email
            send_mail(
                'OTP Verification',
                f'Your OTP is {otp}',
                'praveencodeedex@gmail.com',
                [user.email]
            )
            return user
        else:
            # New user, create account and generate OTP
            username = validated_data['username']
            email = validated_data['email']

            user = User.objects.create_user(
                username=username,
                email=email,
                is_active=False
            )

            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            # Send the new OTP to the user's email
            send_mail(
                'OTP Verification',
                f'Your new OTP is {otp}',
                'praveencodeedex@gmail.com',
                [user.email]
            )

            return user


class OTPVerifySerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    class Meta:
        model = User
        fields = ['email','otp']


class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if not user.is_active:
                raise serializers.ValidationError("This account is not active. Please contact support.")
        except User.DoesNotExist:
            raise serializers.ValidationError("No user is registered with this email.")

        # Generate a new OTP for the user every time they request it
        otp = random.randint(100000, 999999)  # Generate a new 6-digit OTP
        user.otp = str(otp)
        user.otp_generated_at = timezone.now()  # Optionally store the timestamp of the OTP generation
        user.save()

        # Send OTP via email
        send_mail(
            'OTP Verification',
            f'Your OTP is {otp}',
            'praveencodeedex@gmail.com',
            [user.email]
        )

        return value


class VerifyOTPLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        try:
            user = User.objects.get(email=email)

            # Check if the OTP is expired
            if user.is_otp_expired():
                # Generate a new OTP
                new_otp = random.randint(100000, 999999)
                user.otp = new_otp
                user.otp_generated_at = timezone.now()
                user.save()

                # Send the new OTP via email
                send_mail(
                    'New OTP for Login',
                    f'Your new OTP is {new_otp}',
                    'your-email@example.com',
                    [user.email],
                )

                raise serializers.ValidationError("Invalid OTP. A new OTP has been sent to your email.")

            # Check if OTP matches
            if user.otp != otp:
                raise serializers.ValidationError("Invalid OTP.")

            # If OTP matches, log the user in
            if not user.is_active:
                raise serializers.ValidationError("This account is not active. Please contact support.")

        except User.DoesNotExist:
            raise serializers.ValidationError("No user is registered with this email.")

        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    category_image = serializers.ImageField(max_length=None, use_url=True)
    class Meta:
        model = Category
        fields = '__all__'


class CarouselItemSerializer(serializers.ModelSerializer):
    title = serializers.CharField(write_only=True)
    image = serializers.ImageField()
    class Meta:
        model = CarouselItem
        fields = ['id', 'title', 'image',]

class BannerImageSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    banner_image = serializers.ImageField()
    class Meta:
        model = BannerImage
        fields ='__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields =['id','image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Products
        fields = [
            'id', 'product_name', 'product_description', 'price', 'category',
            'isofferproduct', 'offerprice', 'Popular_products', 'discount',
            'created_at', 'newarrival', 'trending_one', 'images', 'uploaded_images'
        ]

    def validate(self, attrs):
        # Ensure that required fields have valid values
        if attrs.get('isofferproduct') and (attrs.get('offerprice') is None or attrs.get('discount') is None):
            raise serializers.ValidationError({
                'offerprice': 'Offer price is required when isofferproduct is True.',
                'discount': 'Discount is required when isofferproduct is True.'
            })
        return attrs

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = Products.objects.create(**validated_data)

        # Create ProductImage objects for uploaded images
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)

        return product

    def update(self, instance, validated_data):
        # Extract uploaded_images from the validated data
        uploaded_images = validated_data.pop('uploaded_images', [])

        # Update other fields of the product
        instance = super().update(instance, validated_data)

        # Add new images to the product
        for image in uploaded_images:
            ProductImage.objects.create(product=instance, image=image)

        return instance

class SingleProductSerializer(serializers.ModelSerializer):
    """
    Serializer for a single product, including images and optional related products.
    """
    images = ProductImageSerializer(many=True, read_only=True)  # Images associated with the product
    related_products = serializers.SerializerMethodField()  # Fetch related products

    class Meta:
        model = Products
        fields = [
            'id', 'product_name', 'product_description', 'price', 'offerprice',
            'isofferproduct', 'discount', 'Popular_products', 'newarrival',
            'trending_one', 'created_at', 'images', 'related_products'
        ]

    def get_related_products(self, obj):
        """
        Fetch products in the same category, excluding the current product.
        """
        related = Products.objects.filter(category=obj.category).exclude(id=obj.id)[:5]
        return [{
            'id': prod.id,
            'product_name': prod.product_name,
            'price': prod.price,
            'offerprice': prod.offerprice,
            'isofferproduct': prod.isofferproduct,
        } for prod in related]

class ProductSearchSerializer(serializers.Serializer):
    search_query = serializers.CharField(max_length=100, required=True)


class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # For user representation
    product = ProductSerializer(read_only=True)  # Product details in the cart
    quantity = serializers.IntegerField()  # Quantity of the product in the cart
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # Final price for the cart item

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'quantity', 'price', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Ensure price is a Decimal
        price = instance.product.offerprice if instance.product.isofferproduct and instance.product.offerprice else instance.product.price
        if price is None:
            price = 0  # Fallback value

        # Ensure quantity is an integer (in case it's a string or None)
        quantity = int(instance.quantity) if instance.quantity else 0  # Default to 0 if None or invalid

        # Calculate total price
        representation['price'] = price * quantity

        return representation

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'payment_method', 'product_ids', 'product_names',
            'total_price', 'status', 'created_at', 'updated_at',
            'order_ids', 'total_cart_items', 'selected_weights',
            'quantities', 'delivery_pin'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_payment_method(self, value):
        """
        Ensure that the payment method is either 'COD' or 'Online'
        """
        if value not in ['COD', 'Online']:
            raise serializers.ValidationError("Invalid payment method.")
        return value







