from rest_framework import serializers

from ...models import ProjectSettings


class ProjectSettingsSerializer(serializers.ModelSerializer):
    launch = serializers.SerializerMethodField()

    class Meta:
        model = ProjectSettings
        fields = (
            'launch',
            'participant_step_feedback_enabled',
            'participant_step_microlearning_enabled',
            'team_communication',
            'directory',
            'advisor_request',
            'ask_to_ecosystem')

    def get_launch(self, obj):
        launch_settings = obj.launch
        launch_settings.pop('fix_password')
        return launch_settings
