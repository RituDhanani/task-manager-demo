from rest_framework import generics, status
from .models import User
from .serializers import (SignupSerializer, LoginSerializer, ChangePasswordSerializer,
                          ResetPasswordOTPRequestSerializer,
                          ResetPasswordOTPConfirmSerializer, UserProfileSerializer,
                          LogoutSerializer)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken



# Signup API View
class SignupAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

# Login API View
class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer

# Refresh Token API View
class RefreshTokenAPIView(TokenRefreshView):
    pass

# Change Password API View
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response(
                {"message": "Password changed successfully"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Password Reset OTP Request API View

class ResetPasswordOTPRequestAPIView(APIView):

    def post(self, request):
        serializer = ResetPasswordOTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"message": "OTP sent to your email"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordOTPConfirmAPIView(APIView):

    def post(self, request):
        serializer = ResetPasswordOTPConfirmSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"message": "Password reset successful"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Profile API View
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


# Logout API View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # optional if you want to require access token

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data['refresh']
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful. Token has been blacklisted."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
