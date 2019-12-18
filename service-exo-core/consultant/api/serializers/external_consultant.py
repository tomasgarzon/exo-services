from rest_framework import serializers

from ...models import Consultant
from .consultant import ThumbnailFieldSerializer


class ExternalConsultantSerializer(
        ThumbnailFieldSerializer, serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name')
    short_name = serializers.CharField(source='user.short_name')
    email = serializers.EmailField(source='user.email')
    user_uuid = serializers.CharField(source='user.uuid')

    class Meta:
        model = Consultant
        fields = [
            'full_name', 'short_name',
            'email', 'thumbnail', 'user_uuid']
