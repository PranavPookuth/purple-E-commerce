from http.client import HTTPResponse

from django.contrib.auth import login
from django.core.mail import send_mail
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .utils import generate_otp, send_otp_email
from .serializers import *
import random
from rest_framework import generics


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

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)

                # Check if the OTP has expired or not
                if user.is_otp_expired():
                    otp = random.randint(100000, 999999)
                    user.otp = otp
                    user.otp_generated_at = timezone.now()  # Update the timestamp
                    user.save()

                    # Send OTP via email
                    send_mail(
                        'Login OTP',
                        f'Your OTP for login is {otp}',
                        'your-email@example.com',
                        [user.email]
                    )

                    return Response({'message': 'OTP sent to your email.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'OTP is still valid. Please check your email.'},
                                    status=status.HTTP_400_BAD_REQUEST)

            except User.DoesNotExist:
                return Response({'error': 'No user is registered with this email.'}, status=status.HTTP_404_NOT_FOUND)

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

class CategoryCreateView(generics.ListCreateAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializr

    



