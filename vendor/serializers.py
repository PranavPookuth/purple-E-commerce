from rest_framework import serializers
from .models import *
from datetime import datetime
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')  # Get the request object
        if instance.display_image:
            representation['display_image'] = request.build_absolute_uri(instance.display_image.url)
        return representation

    # Validation for contact_number
    def validate_contact_number(self, value):
        if Vendors.objects.filter(contact_number=value).exists():  # Fixed 'object' to 'objects'
            raise serializers.ValidationError("Vendor with this contact number already exists.")
        return value

    # Validation for whatsapp_number
    def validate_whatsapp_number(self, value):
        if Vendors.objects.filter(whatsapp_number=value).exists():
            raise serializers.ValidationError("A vendor with this WhatsApp number already exists.")
        return value

    # Validation for email
    def validate_email(self, value):
        if Vendors.objects.filter(email=value).exists():
            raise serializers.ValidationError("A vendor with this email already exists.")
        return value

class VendorLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VendorOtpVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
