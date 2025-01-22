from django.shortcuts import render
from rest_framework import status
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from rest_framework.exceptions import AuthenticationFailed
from purple.models import *
from purple.serializers import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated,IsAdminUser
import random
from django.contrib.auth import login


class AdminLoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)  # Log in the user

        return Response({"message": "Admin login successful."}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists. Please choose a different username.'},
                            status=status.HTTP_400_BAD_REQUEST)

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

            # Reset OTP after successful login
            user.otp = None
            user.save()

            # Log in the user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # Include the username in the response
            return Response(
                {
                    "user": user.username,
                    "message": "Login successful!"
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddressAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        """Create a new address, ensuring user_id is provided."""
        if "user" not in request.data:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressUpdateView(generics.UpdateAPIView):
    permission_classes = []  # No authentication required
    authentication_classes = []  # Disable authentication
    queryset = Address.objects.all()  # Fetch all addresses
    serializer_class = AddressSerializer  # Use your AddressSerializer

class UserUpdateView(APIView):
    """
    API view to update user details (name and email).
    """
    permission_classes = []  # Allow access without authentication (if needed)
    authentication_classes = []  # Remove authentication if not required

    def get(self, request):
        """
        Get user details (username, email) excluding superusers.
        """
        users = User.objects.filter(is_superuser=False)  # Exclude superusers
        serializer = UserUpdateSerializer(users, many=True)
        return Response(serializer.data)

    def put(self, request):
        """
        Update user details (username, email).
        """
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User details updated successfully",
                "user": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = []
    authentication_classes = []
    """
    Retrieve or delete a user and their associated addresses.
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get_queryset(self):
        """
        Filter queryset to allow only admins to view user details.
        """
        return User.objects.all()


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return User.objects.filter(is_staff=False, is_superuser=False)