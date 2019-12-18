from rest_framework import serializers


class KeywordSerializer(serializers.Serializer):
    name = serializers.CharField()
    pk = serializers.IntegerField(required=False, allow_null=True)
