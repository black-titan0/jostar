from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserSignupSerializer


class UserSignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]
