from rest_framework import serializers

from ...models import ServiceRequest


class ServiceRequestSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'name',
            'last_name',
            'email',
            'company',
            'position',
            'country',
            'comment',
            'status',
            'motivation',
            'motivation_other',
            'goal',
            'employees',
            'initiatives',
            'book',
        ]
