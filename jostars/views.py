from rest_framework import generics, permissions
from .models import Jostar
from .paginations import JostarPageNumberPagination
from .serializers import CreateJostarSerializer, JostarSerializer


class JostarCreateView(generics.CreateAPIView):
    queryset = Jostar.objects.all()
    serializer_class = CreateJostarSerializer
    permission_classes = [permissions.IsAuthenticated]


class JostarListView(generics.ListAPIView):
    queryset = Jostar.objects.order_by('-created_at').all()
    serializer_class = JostarSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = JostarPageNumberPagination
