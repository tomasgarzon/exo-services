from django.contrib.auth import get_user_model
from rest_framework import serializers

from forum.api.serializers.author import ForumAuthorSerializer
from ...models import QASession


class QASessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QASession
        fields = [
            'pk',
            'name',
            'start_at',
            'end_at',
        ]


class QASessionTeamSerializer(
        QASessionSerializer,
        serializers.ModelSerializer):
    name = serializers.CharField(source='session.name')
    start_at = serializers.DateTimeField(source='session.start_at')
    end_at = serializers.DateTimeField(source='session.end_at')


class QASessionEcosystemSerializer(QASessionSerializer):
    advisors = serializers.SerializerMethodField()

    class Meta:
        model = QASession
        fields = [
            'pk',
            'name',
            'start_at',
            'end_at',
            'advisors',
        ]

    def get_advisors(self, instance):
        adv_list = instance.members.all().values_list(
            'consultant__user', flat=True)
        serializer = ForumAuthorSerializer(
            get_user_model().objects.filter(pk__in=adv_list), many=True)
        return serializer.data
