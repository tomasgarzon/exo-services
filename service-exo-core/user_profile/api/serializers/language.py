from django.conf import settings

from rest_framework import serializers


class LanguagePlattformSerializer(serializers.Serializer):

    platform_language = serializers.ChoiceField(
        choices=settings.LANGUAGES,
    )

    def update(self, instance, validated_data):
        instance.platform_language = validated_data.get('platform_language')
        return instance
