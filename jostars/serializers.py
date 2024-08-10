from rest_framework import serializers
from .models import Jostar, Rating


class CreateJostarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jostar
        fields = ["title", "content"]

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class JostarSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    is_rated = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Jostar
        fields = [
            'id', 'title', 'content',
            'created_at', 'updated_at', 'author_name',
            'number_of_ratings', 'average_rating', 'rating',
            'is_rated',
        ]

    def get_is_rated(self, obj):
        if hasattr(obj, 'user_rating'):
            return obj.user_rating is not None
        return False

    def get_rating(self, obj):
        if hasattr(obj, 'user_rating') and obj.user_rating:
            return obj.user_rating.rating
        return None


class RatingSerializer(serializers.Serializer):
    jostar_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
