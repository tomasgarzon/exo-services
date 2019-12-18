from rest_framework import serializers

from relation.api.serializers.consultant.activity import ConsultantActivitySerializer

from ...models import ConsultantExOProfile


class ConsultantExOProfileSerializer(serializers.ModelSerializer):
    exo_activities = ConsultantActivitySerializer(many=True)

    class Meta:
        model = ConsultantExOProfile
        fields = [
            'availability',
            'availability_hours',
            'exo_activities',
            'personal_mtp',
            'mtp_mastery',
            'video_url',
        ]
