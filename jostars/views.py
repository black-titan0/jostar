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

        # Get the initial queryset for Jostars
        jostars_queryset = Jostar.objects.order_by('-created_at')

        # Apply pagination to get only the Jostars for the current page
        page = self.paginate_queryset(jostars_queryset)

        if page is None:
            # If pagination is not applied, return all Jostars (unlikely in practice)
            return jostars_queryset

        # Prepare lists to keep track of which Jostars need prefetching
        prefetch_ratings_ids = []
        cached_jostars = []

        # Check cache for ratings
        for jostar in page:
            redis_key = f"jr:{user.id}:{jostar.id}"
            rating = RedisProxy.get_cached_value(redis_key)
            if rating is not None:
                # Cache hit: Store the rating on the Jostar object
                jostar.user_rating = [Rating(user=user, jostar=jostar, rating=int(rating))]
                cached_jostars.append(jostar)
            else:
                # Cache miss: Add to prefetch list
                prefetch_ratings_ids.append(jostar.id)

        # Prefetch ratings only for those Jostars where cache was missed
        if prefetch_ratings_ids:
            user_ratings = Rating.objects.filter(user=user, jostar_id__in=prefetch_ratings_ids)
            uncached_jostars = Jostar.objects.filter(id__in=prefetch_ratings_ids).prefetch_related(
                Prefetch(
                    'ratings',
                    queryset=user_ratings,
                    to_attr='user_rating'
                )
            )
            # Combine cached and uncached jostars
            jostars = cached_jostars + list(uncached_jostars)
        else:
            jostars = cached_jostars  # If no prefetch needed, just use cached jostars

        # Ensure `user_rating_obj` is correctly set after prefetching
        for jostar in jostars:
            if hasattr(jostar, 'user_rating_objs') and jostar.user_rating_objs:
                jostar.user_rating_obj = jostar.user_rating_objs[0]

        return jostars


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
