from rest_framework import serializers

from learning.models import TrainingSession

from ....models import ConsultantTrained


class ConsultantTrainedSerializer(serializers.ModelSerializer):

    training_session = serializers.PrimaryKeyRelatedField(queryset=TrainingSession.objects.all())

    class Meta:
        model = ConsultantTrained
        fields = ['id', 'training_session', 'created_by', 'consultant']
