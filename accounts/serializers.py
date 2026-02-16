from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

#signup serializer
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'role',
            'password',
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user

#login serializer
class LoginSerializer(TokenObtainPairSerializer):
    username_field = 'email'
