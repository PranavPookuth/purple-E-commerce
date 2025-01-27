from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from unicodedata import category

from purple.serializers import CategorySerializer
from vendor.serializers import *

from .models import *
from .serializers import *


# Create your views here.
# class ProductCreateView(generics.ListCreateAPIView):
#     permission_classes = []
#     authentication_classes = []
#     queryset = Products.Objects.all()
#     serializer_class = ProductSerializer
#
# class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = []
#     authentication_classes = []
#     queryset = Products.objects.all()
#     serializer_class = ProductSerializer
#

class ProductCreateListView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Products.objects.all()
    serializer_class = ProductCreateSerializer

class ProductCreateDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Products.objects.all()
    serializer_class = ProductCreateSerializer

class ProductListView(generics.ListAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Products.objects.all()
    serializer_class = ProductListSerializer


class SingleProductView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, pk):
        try:
            product = Products.objects.get(pk=pk)
        except Products.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class VendorProductListView(APIView):
    permission_classes = []

    def get(self,request,vendor_id):
        try:
            vendor = Vendors.objects.get(id=vendor_id)
        except Vendors.DoesNotExist:
            return Response({'detail':'Vendor Not Found'},status=status.HTTP_404_NOT_FOUND)

        products=Products.objects.filter(vendor=vendor)
        serializer = ProductCreateSerializer(products,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class VendorCategoryListView(APIView):
    permission_classes = []

    def get(self, request, vendor_id):
        try:
            vendor = Vendors.objects.get(id=vendor_id)  # Ensure vendor exists

            # Fetch unique categories linked to the vendor's products
            categories = Category.objects.filter(products__vendor=vendor).distinct()

            serializer = CategorySerializer(categories, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Vendors.DoesNotExist:
            return Response({"detail": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)


