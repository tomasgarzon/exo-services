from rest_framework import serializers

from utils.models import Stream


class StreamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stream
        fields = ['name', 'code', 'pk']
