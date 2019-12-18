from django.conf import settings

from rest_framework import serializers

from partner.models import Partner
from fastrack.models import FastrackSprint

from ...models import Project


class ServiceCreateSerializer(serializers.ModelSerializer):

    type_project = serializers.ChoiceField(
        choices=settings.PROJECT_AVAILABLE_SERVICES,
    )
    partner = serializers.PrimaryKeyRelatedField(
        queryset=Partner.objects.all(),
        required=False, allow_null=True,
    )

    description = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'customer',
            'type_project',
            'duration',
            'lapse',
            'partner',
            'description',
        ]

    def create(self, validated_data):
        user_from = validated_data.get('user_from')
        customer = validated_data.get('customer')
        partner = validated_data.get('partner')
        name = validated_data.get('name')
        description = validated_data.get('description')
        duration = validated_data.get('duration')
        lapse = validated_data.get('lapse')
        type_project = validated_data.get('type_project')

        if type_project == settings.PROJECT_CH_TYPE_SPRINT_AUTOMATED:
            service = customer.create_sprint_automated(
                user_from=user_from,
                name=name,
                description=description,
                duration=settings.SPRINT_AUTOMATED_STEPS_COUNT,
            )
        elif type_project == settings.PROJECT_CH_TYPE_GENERIC_PROJECT:
            service = customer.create_generic_project(
                user_from=user_from,
                name=name,
                customer=customer,
                duration=duration,
                lapse=lapse)
        elif type_project == settings.PROJECT_CH_TYPE_FASTRACKSPRINT:
            service = FastrackSprint.objects.create_sprint(
                user_from=user_from,
                name=name,
                customer=customer,
                duration=duration,
                lapse=lapse,
                partner=partner,
            )
        service.project_ptr.assign_resources_from_media_library(user_from=user_from)
        return service.project_ptr

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.partner:
            data['partner'] = instance.partner.pk
        return data
