from rest_framework import serializers
from .models import Jostar


class JostarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jostar
        fields = ["title", "content"]

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
