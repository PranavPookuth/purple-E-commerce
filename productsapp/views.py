from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from purple.serializers import CategorySerializer
from vendor.serializers import *
from .models import *
from .serializers import *
from purple.models import *


# Create your views here.
# class ProductCreateView(generics.ListCreateAPIView):
#     permission_classes = []
#     authentication_classes = []
#     queryset = Products.objects.all()
#     serializer_class = ProductSerializer

# class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = []
#     authentication_classes = []
#     queryset = Products.objects.all()
#     serializer_class = ProductSerializer

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

class ProductSearchView(APIView):
    permission_classes = []
    authentication_classes = []

    def search_products(self, search_query):
        """ Helper function to filter products """
        return Products.objects.filter(product_name__icontains=search_query)

    def get(self, request):
        """ Handle GET requests for searching products """
        serializer = ProductSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        search_query = serializer.validated_data['search_query']

        products = self.search_products(search_query)

        if not products.exists():
            return Response({'detail': 'Products Not Found'}, status=status.HTTP_404_NOT_FOUND)

        product_serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(product_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """ Handle POST requests for searching products """
        serializer = ProductSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        search_query = serializer.validated_data['search_query']

        products = self.search_products(search_query)

        if not products.exists():
            return Response({'detail': 'Products Not Found'}, status=status.HTTP_404_NOT_FOUND)

        product_serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(product_serializer.data, status=status.HTTP_200_OK)

class OfferProductsListView(generics.ListAPIView):
    permission_classes = []
    serializer_class = ProductCreateSerializer

    def get_queryset(self):
        # Filter using the correct field 'isofferproduct' instead of 'is_offer_products'
        return Products.objects.filter(isofferproduct=True)

class PopularPorductsListView(generics.ListAPIView):
    permission_classes = []
    serializer_class = ProductCreateSerializer

    def get_queryset(self):
        return Products.objects.filter(Popular_products=True)

class WishlistView(APIView):
    permission_classes = []
    authentication_classes = []
    """
    API to manage Wishlist without authentication
    """


    def get(self, request):
        """
        Get the list of all products in the wishlist.
        """
        wishlist_items = Wishlist.objects.all()  # Fetch wishlist for all users
        serializer = WishlistSerializer(wishlist_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Add a product to the wishlist.
        """
        product_id = request.data.get('product')
        user_id = request.data.get('user')  # User should be explicitly provided

        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the product is already in the wishlist for this user
        if Wishlist.objects.filter(user_id=user_id, product=product).exists():
            return Response({"detail": "Product already in the wishlist."}, status=status.HTTP_400_BAD_REQUEST)

        wishlist_item = Wishlist.objects.create(user_id=user_id, product=product)
        serializer = WishlistSerializer(wishlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        """
        Remove a product from the wishlist.
        """
        product_id = request.data.get('product')
        user_id = request.data.get('user')  # User should be explicitly provided

        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        wishlist_item = Wishlist.objects.filter(user_id=user_id, product=product).first()
        if wishlist_item:
            wishlist_item.delete()
            return Response({"detail": "Product removed from wishlist."}, status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "Product not in the wishlist."}, status=status.HTTP_400_BAD_REQUEST)

class ProductReviewCreateUpdateView(generics.ListCreateAPIView):
    permission_classes = []  # No authentication required
    authentication_classes = []
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer

    def post(self, request, *args, **kwargs):
        """Handles creating a new review"""
        data = request.data.copy()

        if request.user.is_authenticated:
            data['user'] = request.user.id  # Assign user if authenticated
        else:
            data.pop('user', None)  # Ensure 'user' is not sent

        serializer = ProductReviewSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        """Handles partial update of an existing review"""
        review_id = request.data.get("review_id")  # Expecting 'review_id' in request body
        review = get_object_or_404(ProductReview, id=review_id)

        serializer = ProductReviewSerializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

