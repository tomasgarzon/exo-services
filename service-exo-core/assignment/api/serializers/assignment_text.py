from rest_framework import serializers

from ...models import AssignmentText


class AssignmentTextSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignmentText
        fields = [
            'text',
        ]
