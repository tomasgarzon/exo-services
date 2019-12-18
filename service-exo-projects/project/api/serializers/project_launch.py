from rest_framework import serializers

from ...tasks import ProjectLaunchTask


class ProjectLaunchSerializer(serializers.Serializer):
    message = serializers.CharField(
        required=False,
        allow_blank=True, allow_null=True)

    def update(self, project, validated_data):
        user = self.context.get('request').user
        project.sync_launch(user)
        ProjectLaunchTask().s(
            project_id=project.pk,
            message=validated_data.get('message'),
            user_id=user.id).apply_async()
        return project
