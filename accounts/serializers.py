import random
from rest_framework import serializers
from .models import User, PasswordResetOTP
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

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

# Change Password Serializer
User = get_user_model()
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters")
        return value
    

# Password Reset Serializer
User = get_user_model()
class ResetPasswordOTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs['email']

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email not registered")

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Delete old OTPs
        PasswordResetOTP.objects.filter(email=email).delete()

        # Save new OTP
        PasswordResetOTP.objects.create(email=email, otp=otp)

        # Send OTP email
        send_mail(
            "Password Reset OTP",
            f"Your OTP is: {otp}\nIt expires in 5 minutes.",
            None,
            [email],
        )

        return attrs
    
# Password Reset Confirm Serializer
class ResetPasswordOTPConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField()

    def validate(self, attrs):
        email = attrs['email']
        otp = attrs['otp']
        new_password = attrs['new_password']

        try:
            otp_obj = PasswordResetOTP.objects.get(email=email, otp=otp)
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")

        if otp_obj.is_expired():
            otp_obj.delete()
            raise serializers.ValidationError("OTP expired")

        # Set new password
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        otp_obj.delete()  # Remove OTP after use

        return attrs

# User Profile Serializer
User = get_user_model()
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'role']