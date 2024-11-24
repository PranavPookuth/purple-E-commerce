from http.client import HTTPResponse
from django.contrib.auth import login
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import generate_otp, send_otp_email
from .serializers import *
import random
from rest_framework import generics
from . models import *
from rest_framework.filters import SearchFilter

class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []


    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')

        try:
            user = User.objects.get(email=email)

            if user.is_verified:
                return Response({'error': 'User with this email is already verified.'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Check if OTP is expired, and regenerate if necessary
            if user.is_otp_expired():
                otp = random.randint(100000, 999999)
                user.otp = otp
                user.otp_generated_at = timezone.now()  # Set the timestamp
                user.save()

                # Send the new OTP to the user's email
                send_mail(
                    'OTP Verification',
                    f'Your new OTP is {otp}',
                    'praveencodeedex@gmail.com',
                    [user.email]
                )

                return Response({'message': 'A new OTP has been sent to your email. Please verify your OTP.'},
                                status=status.HTTP_200_OK)

            return Response({'message': 'OTP already sent. Please verify your OTP.'},
                            status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # If the user does not exist, create a new user
            otp = random.randint(100000, 999999)
            user = User.objects.create_user(
                username=username,
                email=email,
                otp=otp,
                otp_generated_at=timezone.now()
            )

            send_mail(
                'OTP Verification',
                f'Your new OTP is {otp}',
                'praveencodeedex@gmail.com',
                [user.email]
            )

            return Response({"message": "User registered successfully. OTP sent."}, status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    permission_classes = []
    authentication_classes = []


    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            otp = serializer.data['otp']
            try:
                user = User.objects.get(email=email)

                # Check if OTP is expired
                if user.is_otp_expired():
                    new_otp = random.randint(100000, 999999)
                    user.otp = new_otp
                    user.otp_generated_at = timezone.now()  # Reset the timestamp
                    user.save()

                    # Send the new OTP to the user's email
                    send_mail(
                        'OTP Verification',
                        f'Your new OTP is {new_otp}',
                        'praveencodeedex@gmail.com',
                        [user.email]
                    )

                    return Response({'message': 'OTP expired. A new OTP has been sent to your email.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Check if OTP matches
                if user.otp == otp:
                    user.is_verified = True
                    user.is_active = True
                    user.otp = None  # Clear the OTP after successful verification
                    user.save()

                    return Response({'message': 'Email verified successfully! You can now log in.'},
                                     status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestOTPView(APIView):
    permission_classes = []
    authentication_classes = []


    def post(self, request, *args, **kwargs):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "OTP sent successfully!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = VerifyOTPLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            # Clear OTP after successful verification
            user.otp = None
            user.otp_generated_at = None  # Clear the OTP timestamp
            user.save()

            # Specify the backend explicitly
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Use your actual backend if different

            # Log the user in
            login(request, user)

            return Response({'message': 'Login successful!'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer



class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer



class CategoryCreateView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Category.objects.all()
    serializer_class = CategorySerializer




class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class CarouselListCreateView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = CarouselItem.objects.all()
    serializer_class = CarouselItemSerializer
    parser_classes = [MultiPartParser, FormParser]  # Ensure file upload parsing

    def create(self, request, *args, **kwargs):
        images = request.FILES.getlist('image')
        title = request.data.get('title')
        if not title:
            return Response(
                {"error": "title  & image is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not images:
            return Response(
                {"error": "At least one image is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data_list = []
        for image in images:
            # Pass the image and title to the serializer
            data = {
                'title': title,
                'image': image
            }
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()  # Save the instance
            data_list.append(serializer.data)

        return Response(data_list, status=status.HTTP_201_CREATED)


class CarouselDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = CarouselItem.objects.all()
    serializer_class = CarouselItemSerializer

class BannerImageListCreateView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = BannerImage.objects.all()
    serializer_class = BannerImageSerializer


class BannerDetailsView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = BannerImage.objects.all()
    serializer_class = BannerImageSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Products.objects.all()
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Handle GET request to retrieve a product
        """
        try:
            product = self.get_object()
            serializer = self.get_serializer(product)
            return Response({
                'message': 'Product retrieved successfully!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response({'error':  'Product not found!'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """
        Handle PUT or PATCH request to update a product
        """
        partial = kwargs.pop('partial', False)
        try:
            product = self.get_object()
            serializer = self.get_serializer(product, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                'message': 'Product updated successfully!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response({'error': 'Product not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Handle DELETE request to delete a product
        """
        try:
            product = self.get_object()
            self.perform_destroy(product)
            return Response({
                'message': 'Product deleted successfully!'
            }, status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response({'error': 'Product not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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

class ProductImageDetailView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve a product image by ID.
        """
        product_image = get_object_or_404(ProductImage, pk=pk)
        serializer = ProductImageSerializer(product_image)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk, *args, **kwargs):
        """
        Add new images to an existing product via PATCH method.
        """
        product = get_object_or_404(Products, pk=pk)

        # Extract multiple images from the request
        uploaded_images = request.FILES.getlist('uploaded_images')

        if uploaded_images:
            # Add each image to the product
            for image in uploaded_images:
                ProductImage.objects.create(product=product, image=image)

        # Serialize the updated product
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        """
        Replace existing images or add new ones via PUT method.
        """
        product = get_object_or_404(Products, pk=pk)

        # Extract multiple images from the request
        uploaded_images = request.FILES.getlist('uploaded_images')

        if uploaded_images:
            # Clear existing images
            ProductImage.objects.filter(product=product).delete()

            # Add new images
            for image in uploaded_images:
                ProductImage.objects.create(product=product, image=image)

        # Update other product fields if needed
        serializer = ProductSerializer(product, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """
        Delete a product image by ID.
        """
        product_image = get_object_or_404(ProductImage, pk=pk)
        product_image.delete()
        return Response({"message": "Product image deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class SingleProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Products.objects.all()
    serializer_class = SingleProductSerializer

class ProductSearchView(APIView):
    permission_classes = []
    authentication_classes = []
    """
    API View to handle product search using a search_query parameter.
    """
    def post(self, request, *args, **kwargs):
        # Validate the incoming data
        input_serializer = ProductSearchSerializer(data=request.data)
        if input_serializer.is_valid():
            search_query = input_serializer.validated_data.get('search_query')

            # Perform search on the Products model
            results = Products.objects.filter(
                product_name__icontains=search_query
            ) | Products.objects.filter(
                product_description__icontains=search_query
            )

            # Serialize the results
            output_serializer = ProductSerializer(results, many=True)
            return Response({
                'message': f'{len(results)} products found.',
                'results': output_serializer.data
            }, status=status.HTTP_200_OK)

        # Return validation errors if input is invalid
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

1234





