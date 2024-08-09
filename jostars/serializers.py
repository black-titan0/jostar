from rest_framework import serializers
from .models import Jostar


class CreateJostarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jostar
        fields = ["title", "content"]

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class JostarSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Jostar
        fields = [
            'id', 'title', 'content',
            'created_at', 'updated_at', 'author_name',
            'number_of_ratings', 'average_rating',
        ]
