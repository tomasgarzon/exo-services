from django.conf import settings

from rest_framework import serializers

from utils.drf.serializers import TimezoneField
from utils.dates import find_timezone
from ...models import Project
from ...helpers import next_project_url
from ...signals import project_status_signal


class NextUrlSerializerMixin(serializers.ModelSerializer):
    next_url = serializers.SerializerMethodField()

    def get_next_url(self, obj):
        user = self.context.get('request').user
        return next_project_url(obj, user)[0]


class ProjectListSerializer(
        NextUrlSerializerMixin,
        serializers.ModelSerializer):

    can_edit = serializers.SerializerMethodField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    timezone = TimezoneField()

    class Meta:
        model = Project
        fields = [
            'uuid',
            'pk',
            'name',
            'start',
            'end',
            'status',
            'location',
            'timezone',
            'place_id',
            'next_url',
            'type',
            'profile_url',
            'comment',
            'can_edit',
        ]

    def get_can_edit(self, obj):
        user = self.context.get('request').user
        return obj.has_perm(user, settings.PROJECT_PERMS_PROJECT_MANAGER)


class ProjectUpdateSerializer(NextUrlSerializerMixin, serializers.ModelSerializer):
    place_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Project
        fields = [
            'name',
            'start',
            'end',
            'comment',
            'location',
            'place_id',
            'uuid',
            'slug',
            'pk',
            'profile_url',
            'next_url',
            'status',
        ]
        read_only_fields = (
            'uuid',
            'slug',
            'pk',
            'profile_url',
            'status',
        )

    def update(self, instance, validated_data):
        user_from = validated_data.pop('user_from')
        instance.check_edit_perms(user_from)
        instance = super().update(instance, validated_data)

        place_id = validated_data.get('place_id')

        if place_id:
            timezone = find_timezone(place_id)
            instance.timezone = timezone
            instance.save(update_fields=['timezone'])

        project_status_signal.send(
            sender=Project,
            instance=instance
        )
        return instance


class ProjectRetrieveSerializer(NextUrlSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            'name',
            'start',
            'end',
            'location',
            'place_id',
            'comment',
            'uuid',
            'slug',
            'pk',
            'profile_url',
            'next_url',
            'comment',
            'status',
        ]
