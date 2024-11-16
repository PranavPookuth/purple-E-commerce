from rest_framework import serializers
from .models import *
from .utils import generate_otp, send_otp_email



class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

    def create(self, validated_data):
        # Generate OTP
        otp = generate_otp()

        # Send OTP via email
        send_otp_email(validated_data['email'], otp)

        # Create user with OTP
        user = User.objects.create_user(
            email=validated_data['email'],
            otp=otp,
            username=validated_data.get('username', '')
        )
        return user

class OTPVerifySerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    class Meta:
        model = User
        fields = ['email','otp']