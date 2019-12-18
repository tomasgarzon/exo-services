from rest_framework import serializers

from consultant.models import Consultant

from ...models import Team


class TeamStepSerializer(serializers.ModelSerializer):
    coach_name = serializers.CharField(source='coach.user.full_name')
    coach_slug = serializers.CharField(source='coach.user.slug')

    class Meta:
        model = Team
        fields = [
            'name',
            'coach_name',
            'coach_slug',
        ]


class TeamUserMemberSerializer(serializers.Serializer):
    short_name = serializers.CharField()
    email = serializers.EmailField()


class TeamSerializer(serializers.ModelSerializer):
    coach = serializers.PrimaryKeyRelatedField(queryset=Consultant.objects.all())
    team_members = TeamUserMemberSerializer(many=True)
    zoom_id = serializers.CharField(allow_blank=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'stream', 'coach', 'team_members',
            'zoom_id',
        ]

    def get_fields(self):
        fields = super().get_fields()
        project = self._context.get('view').get_project()
        fields['coach'].queryset = project.consultants_roles.get_team_manager_consultants(project).consultants()
        return fields

    def validate_zoom_id(self, value):
        if value:
            return value.replace('-', '')
        return value

    def create(self, validated_data):
        team = Team.objects.create(
            user_from=validated_data.get('user_from'),
            project=validated_data.get('project'),
            name=validated_data.get('name'),
            coach=validated_data.get('coach'),
            zoom_id=validated_data.get('zoom_id'),
            stream=validated_data.get('stream'),
            team_members=validated_data.get('team_members'),
            created_by=self.context.get('request').user,
        )
        return team

    def update(self, instance, validated_data):
        team = Team.objects.update(
            instance=instance,
            user_from=validated_data.get('user_from'),
            name=validated_data.get('name'),
            coach=validated_data.get('coach'),
            zoom_id=validated_data.get('zoom_id'),
            stream=validated_data.get('stream'),
            team_members=validated_data.get('team_members'),
        )
        return team
