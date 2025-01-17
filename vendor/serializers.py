from rest_framework import serializers
from .models import *
from datetime import datetime
from django.conf import settings


from rest_framework import serializers
from .models import Vendors

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendors
        fields = [
            'id',
            'name',
            'contact_number',
            'whatsapp_number',
            'email',
            'otp',
            'display_image',
            'is_active',
            'is_approved',
            'otp_expiry',
            'created_at',
            'is_fully_active',
        ]
        read_only_fields = ['id', 'created_at', 'is_fully_active']

        def validate_conatct_number(self,value):
            if Vendors.object.filter(contact_number=value).exist():
                raise serializers.ValidationError("vendor with this contact number already exist")
            return value

        def validate_whatsapp_number(self, value):
            if Vendors.objects.filter(whatsapp_number=value).exists():
                raise serializers.ValidationError("A vendor with this WhatsApp number already exists.")
            return value

        def validate_email(self, value):
            if Vendors.objects.filter(email=value).exists():
                raise serializers.ValidationError("A vendor with this email already exists.")
            return value

class VendorLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VendorOtpVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
