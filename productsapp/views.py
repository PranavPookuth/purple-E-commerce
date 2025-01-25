
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from .models import *
from .serializers import *


# Create your views here.

class ProductListView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

class ProductDetailsView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

class ProductImageListView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def post(self, request, product_id, *args, **kwargs):
        """
        Create multiple product images for a given product.
        """
        product = get_object_or_404(Products, id=product_id)

        # Loop over the uploaded images and save them
        images = request.FILES.getlist('image')  # 'image' is the key in form-data
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        return Response({"message": "Images uploaded successfully"}, status=status.HTTP_201_CREATED)
