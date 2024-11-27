import string
from decimal import Decimal
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
from django.db.models import Sum, F
from decimal import Decimal
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


class AddToCartView(APIView):
    permission_classes = []
    authentication_classes = []
    def post(self, request, user_id, product_id):
        # Get the user and product or return a 404 if not found
        user = get_object_or_404(User, pk=user_id)
        product = get_object_or_404(Products, pk=product_id)

        # Get the quantity from the request data (defaults to 1 if not provided)
        quantity = request.data.get('quantity', 1)

        # Determine the price based on whether the product has an offer
        if product.isofferproduct and product.offerprice:
            price = product.offerprice
        else:
            price = product.price

        # Try to get or create the cart item
        cart_item, created = Cart.objects.get_or_create(user=user, product=product)

        if created:
            cart_item.quantity = quantity
            cart_item.price = price  # Set the price for the cart item
            cart_item.save()

            # Serialize the cart item and return a response
            serializer = CartSerializer(cart_item, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If the item is already in the cart, return a message
        else:
            return Response({"detail": "Item already in cart, no changes made"}, status=status.HTTP_200_OK)


class UpdateCartItemQuantityView(APIView):
    permission_classes = []
    authentication_classes = []
    def put(self, request, user_id, product_id):
        return self.update_cart_item(request, user_id, product_id, partial=False)

    def patch(self, request, user_id, product_id):
        return self.update_cart_item(request, user_id, product_id, partial=True)

    def update_cart_item(self, request, user_id, product_id, partial):
        user = get_object_or_404(User, pk=user_id)
        product = get_object_or_404(Products, pk=product_id)

        # Get the new quantity from the request data
        quantity = request.data.get('quantity')

        # Validate the quantity
        if not partial or 'quantity' in request.data:
            if quantity is None or not str(quantity).isdigit() or int(quantity) < 1:
                return Response({"detail": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the cart item for this user and product
        cart_item = get_object_or_404(Cart, user=user, product=product)

        # Determine the price to apply (offer price or regular price)
        if product.isofferproduct and product.offerprice:
            price = product.offerprice  # Use the offer price if available
        else:
            price = product.price  # Otherwise, use the regular price

        # Update the cart item's quantity and price
        if quantity:
            cart_item.quantity = int(quantity)

        cart_item.price = price
        cart_item.total_price = cart_item.quantity * cart_item.price  # Update the total price based on quantity

        # Save the updated cart item
        cart_item.save()

        # Recalculate the total cart price for the user
        total_cart_price = Cart.objects.filter(user=user).aggregate(total=Sum(F('quantity') * F('price')))['total']

        # Serialize the updated cart item and return a response
        serializer = CartSerializer(cart_item, context={'request': request})

        # Return the updated cart item and total price
        response_data = {
            'cart_item': serializer.data,
            'total_cart_price': total_cart_price
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UserCartView(APIView):
    permission_classes = []
    authentication_classes = []
    def get(self, request, user_id):
        # Fetch cart items for the user
        cart_items = Cart.objects.filter(user_id=user_id).select_related('product')

        # Initialize total cart price
        total_cart_price = Decimal('0.00')

        # Iterate over the cart items and calculate the total price
        for cart_item in cart_items:
            product = cart_item.product

            # Determine the price to use (offer price if available, else regular price)
            if product.isofferproduct and product.offerprice:
                price = product.offerprice
            else:
                price = product.price

            # Calculate the total price for this cart item based on the quantity
            cart_item.total_price = cart_item.quantity * price

            # Add this cart item's total price to the total cart price
            total_cart_price += cart_item.total_price

        # Serialize the cart items to include in the response
        serializer = CartSerializer(cart_items, context={'request': request}, many=True)

        # Prepare the response data
        response_data = {
            'message': 'Products Retrieved Successfully',
            'cart_items': serializer.data,
            'total_cart_price': str(total_cart_price)  # Convert to string for precision
        }

        return Response(response_data, status=status.HTTP_200_OK)


class RemoveFromCartView(APIView):
    permission_classes = []
    authentication_classes = []
    def delete(self, request, user_id, product_id):
        # Get the user and product
        user = get_object_or_404(User, pk=user_id)
        product = get_object_or_404(Products, pk=product_id)

        # Try to get the cart item
        cart_item = get_object_or_404(Cart, user=user, product=product)

        # Delete the cart item
        cart_item.delete()

        return Response({"message": "Product removed from cart"}, status=status.HTTP_204_NO_CONTENT)

class CheckoutCODView(APIView):
    permission_classes = []
    authentication_classes = []  # Define appropriate permission classes as needed

    def generate_order_id(self):
        """Generate a unique order ID."""
        prefix = "ORD"
        random_number = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{random_number}"

    def generate_delivery_pin(self):
        """Generate a 4-digit random delivery pin."""
        return ''.join(random.choices(string.digits, k=4))

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_404_NOT_FOUND)

        # Collect address data from the request body
        address = request.data.get('address')
        city = request.data.get('city')
        state = request.data.get('state')
        pin_code = request.data.get('pin_code')

        if not all([address, city, state, pin_code]):
            return Response({"error": "address, city, state, and pin_code are required"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = 0
        total_cart_items = cart_items.count()
        product_ids = []
        product_names = []
        quantities = []

        # Iterate over the cart items to calculate the total price and collect product data
        for cart_item in cart_items:
            product = cart_item.product  # Assuming each cart item has a reference to a product

            # No stock check needed, just proceed with the quantity in the cart item
            total_price += product.price * cart_item.quantity  # Assuming product has a 'price' attribute
            product_ids.append(str(product.id))
            product_names.append(product.product_name)  # Use 'product_name' instead of 'name'
            quantities.append(str(cart_item.quantity))

        # Generate unique order ID and delivery pin
        unique_order_id = self.generate_order_id()
        delivery_pin = self.generate_delivery_pin()

        # Create the order with the 'COD' payment method
        order = Order.objects.create(
            user=user,
            payment_method='COD',
            product_ids=",".join(product_ids),
            product_names=",".join(product_names),
            total_price=total_price,
            total_cart_items=total_cart_items,
            quantities=",".join(quantities),
            order_ids=unique_order_id,
            delivery_pin=delivery_pin,
            address=address,
            city=city,
            state=state,
            pin_code=pin_code
        )

        # Clear the user's cart after the order is placed
        cart_items.delete()

        return Response({
            "message": "Checkout successful",
            "total_price": total_price,
            "total_cart_items": total_cart_items,
            "order_id": order.order_ids,
            "delivery_pin": delivery_pin
        }, status=status.HTTP_201_CREATED)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Order.objects.filter(user_id=user_id).order_by('-created_at')




