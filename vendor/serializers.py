from rest_framework import serializers
from .models import *
from datetime import datetime
from django.conf import settings


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
