from rest_framework import serializers

from files.api.serializers.uploaded_file_reverse import UploadedFileRelatedGenericSerializer

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

    def get_deliverables(self, obj):
        user_from = self.context.get('request').user
        team = self.context.get('view').team
        assignment_step_team = obj.assignment_step_teams.get(team=team)
        files = assignment_step_team.uploaded_files_with_visibility(user_from)
        return UploadedFileRelatedGenericSerializer(files, many=True, context=self.context).data
