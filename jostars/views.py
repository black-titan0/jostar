from rest_framework import generics, permissions
from .models import Jostar
from .serializers import JostarSerializer


class JostarCreateView(generics.CreateAPIView):
    queryset = Jostar.objects.all()
    serializer_class = JostarSerializer
    permission_classes = [permissions.IsAuthenticated]
