from rest_framework import serializers

from project.models import Project
from consultant.models import Consultant

from ...models import QASession, QASessionTeam


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name']


class ConsultantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultant
        fields = ['id']


class QASessionTeamSerializer(serializers.ModelSerializer):
    url = serializers.CharField()

    class Meta:
        model = QASessionTeam
        fields = ['team', 'url', 'id']


class QASessionSerializer(serializers.ModelSerializer):
    url = serializers.CharField()
    project = ProjectSerializer()
    consultants = ConsultantSerializer(
        many=True, source='advisors.consultants')
    teams = QASessionTeamSerializer(many=True)

    class Meta:
        model = QASession
        fields = '__all__'
