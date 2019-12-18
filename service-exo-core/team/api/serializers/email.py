from rest_framework import serializers

from ...models import Team


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['id']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False},
        }


class TeamEmailSerializer(serializers.Serializer):
    subject = serializers.CharField()
    message = serializers.CharField()
    teams = TeamSerializer(many=True)
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
    )

    def get_fields(self):
        fields = super().get_fields()
        project = self._context.get_project()
        fields['teams'].queryset = Team.objects.filter_by_project(project)
        return fields
