from rest_framework import serializers

from exo_certification.api.serializers.certification_role import CertificationRoleSerializer

from ...models import Consultant


class ThumbnailFieldSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    def get_thumbnail(self, obj):
        return obj.user.profile_picture.get_thumbnail_url()


class ConsultantSimpleSerializer(
        ThumbnailFieldSerializer, serializers.ModelSerializer):
    user_id = serializers.CharField(source='user.pk')
    user_uuid = serializers.CharField(source='user.uuid')
    name = serializers.CharField(source='user.get_full_name')
    email = serializers.EmailField(source='user.email')
    url_profile = serializers.CharField(source='get_public_profile_v2')
    user_title = serializers.CharField(source='user.user_title')
    certifications = serializers.SerializerMethodField()

    class Meta:
        model = Consultant
        fields = [
            'id', 'user_uuid', 'user_id',
            'name', 'email',
            'user_title',
            'thumbnail',
            'url_profile',
            'status',
            'certifications',
        ]

    def get_certifications(self, obj):
        return CertificationRoleSerializer(
            obj.certification_roles.all(),
            many=True,
            context={'user': obj.user}
        ).data


class PublicConsultantSerializer(
        ThumbnailFieldSerializer,
        serializers.ModelSerializer
):
    short_name = serializers.CharField(source='user.short_name')
    full_name = serializers.CharField(source='user.full_name')
    location = serializers.CharField(source='user.location')
    short_me = serializers.CharField(source='user.short_me')
    about_me = serializers.CharField(source='user.about_me')

    class Meta:
        model = Consultant
        fields = [
            'short_name', 'full_name', 'thumbnail',
            'location', 'short_me', 'about_me',
        ]


class WebStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Consultant
        fields = ['showing_web']

    def update(self, instance, validated_data):
        instance.showing_web = validated_data.get('showing_web')
        return validated_data
