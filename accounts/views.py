from rest_framework import generics
from .models import User
from .serializers import SignupSerializer, LoginSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# Signup API View
class SignupAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

# Login API View
class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer