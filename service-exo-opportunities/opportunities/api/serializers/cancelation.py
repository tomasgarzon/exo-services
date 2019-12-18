from rest_framework import serializers


class CancelationSerializer(serializers.Serializer):
    comment = serializers.CharField(
        required=False, allow_null=True, allow_blank=True,
    )

    class Meta:
        fields = ['comment']
