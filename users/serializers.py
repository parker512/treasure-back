# yourapp/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from media.models import Photo

User = get_user_model()

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'image']  # или другие поля, если есть

class UserSerializer(serializers.ModelSerializer):
    avatar = PhotoSerializer(read_only=True)
    avatar_id = serializers.PrimaryKeyRelatedField(
        queryset=Photo.objects.all(), source='avatar',
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'birth_date', 'region', 'city', 'phone_number', 'avatar', 'avatar_id')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'birth_date', 'region', 'city', 'phone_number')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)