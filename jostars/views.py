import json

from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from Jostar import settings
from proxies.kafka import KafkaProxy
from proxies.redis import RedisProxy
from .models import Jostar, Rating
from .paginations import JostarPageNumberPagination
from .serializers import CreateJostarSerializer, JostarSerializer
from rest_framework.response import Response
from .serializers import RatingSerializer


class JostarCreateView(generics.CreateAPIView):
    queryset = Jostar.objects.all()
    serializer_class = CreateJostarSerializer
    permission_classes = [IsAuthenticated]


class JostarListView(generics.ListAPIView):
    queryset = Jostar.objects.order_by('-created_at').all()
    serializer_class = JostarSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = JostarPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        user_ratings = Rating.objects.filter(user=user).filter(is_deleted=False)
        return Jostar.objects.order_by('-created_at').all().prefetch_related(
            Prefetch(
                'ratings',
                queryset=user_ratings,
                to_attr='user_rating'
            )
        )


class RateJostarView(views.APIView):
    permissions = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Submit a rating for a Jostar.",
        request_body=RatingSerializer,
    )
    def post(self, request):
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            message = {
                'user_id': request.user.id,
                'jostar_id': data['jostar_id'],
                'rating': data['rating']
            }
            redis_key = f"jr:{request.user.id}:{data['jostar_id']}"
            already_cached_value = RedisProxy.get_cached_value(redis_key)
            if already_cached_value and int(already_cached_value) == data['rating']:
                return Response(
                    {"message": "Jostar is Already Rated!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            RedisProxy.cache_with_ttl(key=redis_key, value=data['rating'])
            message_str = json.dumps(message)

            KafkaProxy.simple_produce_to_topic(
                key=str(request.user.id), value=message_str,
                topic=settings.JOSTARS_RATING_KAFKA_TOPIC,
            )

            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
