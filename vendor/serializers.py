from rest_framework import serializers
from .models import *
from datetime import datetime
from django.conf import settings


class VendorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendors
        fields = '__all__'
