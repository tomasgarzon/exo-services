from django.conf import settings

from rest_framework import serializers

from ...models import (
    InformationBlock, AssignmentAdviceItem,
    AssignmentTaskItem, AssignmentText, AssignmentResourceItem)
from .assignment_text import AssignmentTextSerializer
from .assignment_advice_item import AssignmentAdviceItemSerializer
from .assignment_resource_item import AssignmentResourceItemSerializer


class InformationBlockSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    class Meta:
        model = InformationBlock
        fields = [
            'pk',
            'type',
            'title',
            'subtitle',
            'order',
            'contents',
            'section',
        ]

    def get_contents(self, obj):
        # Mandatory to be here to avoid recursivity
        from .assignment_task_item import AssignmentTaskItemSerializer

        contents = []

        if obj.type == settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPE_TEXT:
            items = AssignmentText.objects.filter(block=obj)
            contents = AssignmentTextSerializer(items, many=True).data
        elif obj.type == settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPE_ADVICE:
            items = AssignmentAdviceItem.objects.filter(assignment_advice__block=obj)
            contents = AssignmentAdviceItemSerializer(items, many=True).data
        elif obj.type == settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPE_TASK:
            items = AssignmentTaskItem.objects.filter(assignment_task__block=obj)
            contents = AssignmentTaskItemSerializer(items, many=True, context=self.context).data
        elif obj.type == settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPE_RESOURCE:
            items = AssignmentResourceItem.objects.filter(assignment_resource__block=obj)
            contents = AssignmentResourceItemSerializer(items, many=True).data

        return contents
