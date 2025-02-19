import pytz
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from .models import *
from django.core.mail import send_mail
import random
import uuid
from django.utils import timezone


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Authenticate the user using email and password
        user = authenticate(request=self.context.get('request'), email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials.")

        # Ensure the user is an admin
        if not user.is_superuser:
            raise PermissionDenied("User is not an admin.")

        data['user'] = user
        return data


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
        fields = ['email', 'otp']

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        try:
            user = User.objects.get(email=email)

            # Check if OTP is expired
            if user.is_otp_expired():
                raise serializers.ValidationError("OTP has expired. Please request a new OTP.")

            # Do NOT regenerate OTP if it's incorrect
            if user.otp != otp:
                raise serializers.ValidationError("Invalid OTP. Please enter the correct OTP.")

            # If OTP is correct, verify the user
            user.otp = None
            user.otp_generated_at = None
            user.is_verified = True
            user.is_active = True
            user.save()

        except User.DoesNotExist:
            raise serializers.ValidationError("No user is registered with this email.")

        return data



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

            # Check if OTP is expired
            if user.is_otp_expired():
                new_otp = random.randint(100000, 999999)
                user.otp = new_otp
                user.otp_generated_at = timezone.now()
                user.save()

                # Send the new OTP via email
                send_mail(
                    'New OTP for Login',
                    f'Your new OTP is {new_otp}',
                    'praveencodeedex@gmail.com',
                    [user.email],
                )

                raise serializers.ValidationError("OTP has expired. A new OTP has been sent to your email.")

            # If OTP is incorrect, regenerate and send a new OTP
            if user.otp != otp:
                new_otp = random.randint(100000, 999999)  # Generate new OTP
                user.otp = new_otp
                user.otp_generated_at = timezone.now()  # Update the generation timestamp
                user.save()

                # Send the new OTP via email
                send_mail(
                    'New OTP for Login',
                    f'Your new OTP is {new_otp}',
                    'praveencodeedex@gmail.com',
                    [user.email],
                )

                raise serializers.ValidationError("Invalid OTP. A new OTP has been sent to your email.")

            # If OTP is correct, proceed with login
            user.otp = None  # Clear the OTP after successful login
            user.save()

        except User.DoesNotExist:
            raise serializers.ValidationError("No user is registered with this email.")

        return data


User = get_user_model()

class AddressSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(write_only=True)
    class Meta:
        model = Address
        fields = '__all__'  # Include all fields
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        """Assign user instance instead of user_id."""
        user = validated_data.pop('user')  # Extract the user_id from validated data
        user = User.objects.get(id=user)  # Retrieve the User instance using the ID
        return Address.objects.create(user=user, **validated_data)



class UserDetailSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id','username', 'email',
            'is_verified', 'is_active', 'is_staff',
             'addresses'
        ]


class UserListSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'is_verified', 'is_active', 'is_staff',
            'date_joined', 'addresses'
        ]

User = get_user_model()

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # Referring to the CustomUser model
        fields = ['username', 'email']

    def validate_email(self, value):
        # Add custom validation if needed
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("This email is already associated with another account.")
        return value

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

        def validate_category_image(self, value):
            if value.size > 5 * 1024 * 1024:  # 5MB limit
                raise serializers.ValidationError("Image file is too large. Maximum size is 5MB.")
            return value

class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = '__all__'



