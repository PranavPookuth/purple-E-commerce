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
    class Meta:
        model = Category
        fields = '__all__'

class BannerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerImage
        fields = '__all__'

class CausorelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaruoselItem
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'



