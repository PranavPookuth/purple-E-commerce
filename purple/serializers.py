import random

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email','otp')

    def create(self, validated_data):
        otp = str(random.randint(100000, 999999))
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            otp = otp
        )
        return user




