from rest_framework import generics
from .models import User
from .serializers import SignupSerializer


class SignupAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

