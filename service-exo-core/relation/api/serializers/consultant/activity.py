from rest_framework import serializers

from exo_activity.models import ExOActivity

from ....models import ConsultantActivity


class ExOActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExOActivity
        fields = [
            'code',
            'description',
            'name',
            'order',
        ]
        ref_name = 'ExOActivitySerializerConsultant'


class ConsultantActivitySerializer(serializers.ModelSerializer):
    exo_activity = ExOActivitySerializer()

    class Meta:
        model = ConsultantActivity
        fields = [
            'status',
            'exo_activity',
        ]
