from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import *
import random


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.otp = self.generate_otp()
            user.save()
            self.send_otp(user.email, user.otp)
            return Response({"message": "User registered successfully. OTP sent."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_otp(self):
        return str(random.randint(100000, 999999))

    def send_otp(self, email, otp):
        # Simulate sending OTP via email
        print(f"OTP for {email}: {otp}")



