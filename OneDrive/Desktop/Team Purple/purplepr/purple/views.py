from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .utils import generate_otp, send_otp_email
from .serializers import *
import random


class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')

        try:
            user = User.objects.get(email=email)

            if user.is_verified:
                return Response({'error': 'User with this email is already verified.'},
                                status=status.HTTP_400_BAD_REQUEST)
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            # Send the new OTP to the user's email
            send_mail(
                'OTP Verification',
                f'Your new OTP is {otp}',
                'praveencodeedex@gmail.com',  # Use your actual email address here
                [user.email]
            )

            self.create_notification(user.name)

            return Response({'message': 'A new OTP has been sent to your email. Please verify your OTP.'},
                            status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # If the user does not exist, create a new user
            otp = generate_otp()
            user = User.objects.create_user(
                username=username,
                email=email,
                otp=otp
            )

            send_otp_email(user.email, otp)
            return Response({"message": "User registered successfully. OTP sent."}, status=status.HTTP_201_CREATED)

        # If the email already exists, this block will never be executed due to the try-except
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()

            # Send the new OTP to the user's email
            send_mail(
                'OTP Verification',
                f'Your new OTP is {otp}',
                'praveencodeedex@gmail.com',  # Use your actual email address here
                [user.email])

            self.create_notification(user.name)

            return Response({'message': 'OTP Sent successfully! Please verify your OTP.'},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            otp = serializer.data['otp']
            try:
                # Find the user by email
                user = User.objects.get(email=email)

                # Check if the OTP provided is correct
                if user.otp == otp:
                    # OTP is correct, mark the user as verified and active
                    user.is_active = True
                    user.is_verified = True
                    user.otp = None  # Clear the OTP after verification
                    user.save()
                    return Response({'message': 'Email verified successfully! You can now log in.'},
                                    status=status.HTTP_200_OK)

                else:
                    # OTP is invalid, generate a new OTP
                    new_otp = random.randint(100000, 999999)
                    user.otp = new_otp
                    user.save()

                    # Send the new OTP to the user's email
                    send_mail(
                        'OTP Verification',
                        f'Your new OTP is {new_otp}',
                        'praveencodeedex@gmail.com',
                        [user.email]
                    )

                    return Response({'message': 'Invalid OTP. A new OTP has been sent to your email.'},
                                    status=status.HTTP_400_BAD_REQUEST)

            except User.DoesNotExist:
                # If user with the given email does not exist
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # If the serializer data is invalid (not provided correctly)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


