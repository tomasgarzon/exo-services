from rest_framework import serializers

from files.api.serializers import UploadedFileRelatedGenericSerializer

from ...models import AssignmentStep
from .information_block import InformationBlockSerializer


class AssignmentStepSerializer(serializers.ModelSerializer):
    blocks = InformationBlockSerializer(many=True)
    deliverables = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentStep
        fields = [
            'pk',
            'name',
            'blocks',
            'deliverables',
        ]

    def _get_team_pk(self):
        return self.context.get('request').parser_context.get('kwargs').get('team_id')

    def get_deliverables(self, obj):
        user_from = self.context.get('request').user
        assignment_step_team = obj.assignment_step_teams.get(team_id=self._get_team_pk())
        files = assignment_step_team.uploaded_files_with_visibility(user_from)
        return UploadedFileRelatedGenericSerializer(files, many=True, context=self.context).data
