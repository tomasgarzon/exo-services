from rest_framework import serializers


class RequestSummitSerializer(serializers.Serializer):

    comment = serializers.CharField()
