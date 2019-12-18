from rest_framework import serializers

from ...models import ProjectSettings


class ProjectSettingsSerializer(serializers.ModelSerializer):
    tickets_module_enabled = serializers.BooleanField(
        source='advisor_request')
    swarm_sessions_module_enabled = serializers.BooleanField(
        source='swarm_session')
    team_communications_module_enabled = serializers.BooleanField(
        source='team_communication')
    ask_ecosystem_enabled = serializers.BooleanField(
        source='ask_to_ecosystem')
    directory_enabled = serializers.BooleanField(
        source='directory')
    quizes_enabled = serializers.BooleanField(
        source='quizes')
    feedback_enabled = serializers.BooleanField(
        source='feedback')

    class Meta:
        model = ProjectSettings
        fields = [
            'tickets_module_enabled', 'swarm_sessions_module_enabled',
            'team_communications_module_enabled', 'ask_ecosystem_enabled',
            'directory_enabled', 'quizes_enabled', 'feedback_enabled']
