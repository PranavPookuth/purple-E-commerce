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
        uploaded_images = validated_data.pop('uploaded_images', [])
        instance = super().update(instance, validated_data)

        if uploaded_images:
            # Clear existing images if needed or add new ones
            ProductImage.objects.filter(product=instance).delete()
            for image in uploaded_images:
                ProductImage.objects.create(product=instance, image=image)
        return instance



