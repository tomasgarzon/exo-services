from rest_framework import serializers

from ...models import AssignmentAdviceItem


class AssignmentAdviceItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignmentAdviceItem
        fields = [
            'pk',
            'description',
            'order',
        ]
