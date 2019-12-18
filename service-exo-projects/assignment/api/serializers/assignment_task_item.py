from rest_framework import serializers, exceptions

from .information_block import InformationBlockSerializer

from ...models import AssignmentTaskItem
from ...conf import settings


class AssignmentTaskItemSerializer(serializers.ModelSerializer):
    blocks = InformationBlockSerializer(many=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentTaskItem
        fields = [
            'pk',
            'name',
            'order',
            'status',
            'blocks',
        ]

    def get_status(self, obj):
        team = self.context.get('view').team
        return obj.get_status(team)


class AssignmentTaskItemListStatusSerializer(serializers.Serializer):
    pk_list = serializers.ListField(required=True)

    class Meta:
        fields = ['pk_list']

    def validate(self, validated_data):
        team = self.context.get('view').team
        user_from = self.context.get('request').user
        is_admin = team.user_is_admin(user_from) or team.project.user_is_admin(user_from)
        if not is_admin and not team.user_is_basic(user_from):
            raise exceptions.ValidationError('{} has no permissions: '.format(user_from))
        return validated_data

    def create(self, validated_data):
        pk_list = validated_data.get('pk_list')
        step = validated_data.get('step')
        team = validated_data.get('team')
        user_from = validated_data.get('user_from')
        new_status = validated_data.get('new_status')
        tasks_items = AssignmentTaskItem.objects.filter(id__in=pk_list)

        for task_item in tasks_items:
            if new_status == settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_TO_DO:
                task_item.mark_as_to_do(user_from=user_from, step=step, team=team)
            elif new_status == settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_DONE:
                task_item.mark_as_done(user_from=user_from, step=step, team=team)

        return tasks_items
