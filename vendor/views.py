from django.shortcuts import render
from . serializers import *
from .models import *
from rest_framework import generics,status


# Create your views here.
class VendorListViews(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Vendors.objects.all()
    serializer_class = VendorSerializer