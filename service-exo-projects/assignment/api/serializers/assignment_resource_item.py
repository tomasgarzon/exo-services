from rest_framework import serializers

from ...models import AssignmentResourceItem


class AssignmentResourceItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignmentResourceItem
        fields = [
            'pk',
            'type',
            'status',
            'name',
            'description',
            'thumbnail',
            'iframe',
            'link',
            'order',
        ]
