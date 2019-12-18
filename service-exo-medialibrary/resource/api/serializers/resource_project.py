from rest_framework import serializers

from ...models import Resource
from ...conf import settings
from .resource_list import ResourceListSerializer


class ResourceProjectMixin(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex_verbose', required=True)

    class Meta:
        model = Resource
        fields = [
            'uuid',
        ]

    def to_representation(self, instance):
        return ResourceListSerializer(instance).data


class ResourceAddProjectSerializer(ResourceProjectMixin):

    def validate_uuid(self, value):
        instance = self.context.get('view').get_object()
        if instance.projects and str(value) in instance.project_list:
            raise serializers.ValidationError('already_assigned')
        return value

    def update(self, instance, validated_data):
        uuid = validated_data.get('uuid')
        instance.project_list = uuid
        return instance


class ResourceRemoveProjectSerializer(ResourceProjectMixin):

    def validate_uuid(self, value):
        instance = self.context.get('view').get_object()
        if not instance.projects or str(value) not in instance.project_list:
            raise serializers.ValidationError('not_assigned')
        return value

    def update(self, instance, validated_data):
        uuid = validated_data.get('uuid')
        project_list = instance.project_list
        project_list.remove(str(uuid))
        instance.projects = ','.join(project_list)
        instance.save(update_fields=['projects'])
        return instance


class ResourcePostSaveProjectSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(format='hex_verbose', required=True)
    type_project_lower = serializers.ChoiceField(choices=settings.RESOURCE_CH_TYPE_PROJECT)

    def create(self, validated_data):
        uuid = validated_data.get('uuid')
        type_project_lower = validated_data.get('type_project_lower')
        section_related_to_type_projects = settings.RESOURCE_RELATION_TYPES_AND_SECTIONS.get(type_project_lower)
        queryset = Resource.objects.filter_by_section(section_related_to_type_projects)
        uuid = str(uuid)
        for resource in queryset:
            if resource.projects:
                if uuid not in resource.project_list:
                    resource.project_list = uuid
            else:
                resource.project_list = uuid

        return queryset
