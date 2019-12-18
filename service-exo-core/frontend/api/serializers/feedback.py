from rest_framework import serializers


class FeedbackSerializer(serializers.Serializer):
    message = serializers.CharField()
    attachment = serializers.FileField(required=False, allow_null=True)
