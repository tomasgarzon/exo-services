from rest_framework import serializers

from ...conf import settings


class InvitationPreviewSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    custom_text = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    validation_type = serializers.ChoiceField(choices=settings.INVITATION_CH_TYPE)
