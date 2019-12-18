from rest_framework import serializers
from django.conf import settings

from customer.models import Customer

from ...models import Project
from ...helpers import next_project_url


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name']


class ProjectSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    type_project = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'pk',
            'name',
            'start',
            'type_project',
            'first_day',
            'customer'
        ]

    def get_type_project(self, obj):
        return obj.type_verbose_name


class ProjectBackofficeSerializer(serializers.ModelSerializer):
    next_url = serializers.SerializerMethodField()
    chat_url = serializers.SerializerMethodField()
    advisor_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'pk', 'uuid', 'name', 'next_url', 'chat_url',
            'advisor_url']

    def get_next_url(self, obj):
        return next_project_url(obj, self.context.get('request').user)

    def _get_team(self, obj):
        teams = obj.teams \
            .filter_by_project(obj) \
            .filter_by_user(obj, self.context.get('request').user)
        if teams:
            team = teams.first()
        else:
            team = obj.teams.first()
        return team

    def get_chat_url(self, obj):
        team = self._get_team(obj)
        return settings.FRONTEND_PROJECT_PAGE.format(
            project_id=obj.pk,
            team_id=team.pk,
            section='team-communication')

    def get_advisor_url(self, obj):
        team = self._get_team(obj)
        return settings.FRONTEND_PROJECT_PAGE.format(
            project_id=obj.pk,
            team_id=team.pk,
            section='requests')
