from django.conf import settings

from rest_framework import serializers

from consultant.models import Consultant, ConsultantExOProfile
from core.models import Language
from exo_activity.models import ExOActivity


class ConsultantProfileLanguagesSerializer(serializers.ModelSerializer):
    languages = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(),
        many=True,
    )

    class Meta:
        model = Consultant
        fields = [
            'languages',
        ]


class ConsultantProfileMTPSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsultantExOProfile
        fields = [
            'personal_mtp', 'mtp_mastery',
        ]


class ConsultantCorePillarsSerializer(serializers.ModelSerializer):

    areas = serializers.MultipleChoiceField(
        allow_blank=True,
        allow_null=True,
        choices=settings.EXO_AREA_CH_EXO_AREAS_NAMES,
    )

    class Meta:
        model = Consultant
        fields = [
            'areas',
        ]

    def update(self, instance, validated_data):
        instance.exo_areas.update_from_values(
            instance,
            validated_data.get('areas', []),
        )
        return instance

    def to_representation(self, instance):
        return {'areas': instance.exo_areas.values_list('exo_area__code', flat=True)}


class ConsultantProfileTimeAvailabilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsultantExOProfile
        fields = [
            'availability',
            'availability_hours',
        ]


class ConsultantProfileActivitiesSerializer(serializers.ModelSerializer):

    exo_activities = serializers.SlugRelatedField(
        queryset=ExOActivity.objects.all(),
        many=True,
        slug_field='code',
    )

    class Meta:
        model = ConsultantExOProfile
        fields = [
            'exo_activities',
        ]

    def update(self, instance, validated_data):
        instance.exo_activities.update_from_values(
            consultant_profile=instance,
            exo_activities=validated_data.get('exo_activities', []),
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        return {'exo_activities': [
            {
                'status': _.status,
                'code': _.exo_activity.code,
            } for _ in instance.exo_activities.all()
        ]}


class ConsultantProfileVideoSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(required=True)

    class Meta:
        model = ConsultantExOProfile
        fields = ['video_url']
