from django.contrib.auth import get_user_model
from rest_framework import serializers

from keywords.serializers import KeywordSerializer
from languages.serializers import LanguageSerializer
from utils.drf.relations import UserUUIDRelatedField
from keywords.models import Keyword
from languages.models import Language
from files.api.serializers.uploaded_file import UploadedFileSerializer

from ...models import Opportunity, OpportunityGroup
from ...ticket_helper import create_opportunity_from_ticket
from .user import UserTaggedSerializer


class HistorySerializer(serializers.Serializer):
    created = serializers.DateTimeField()
    user = UserUUIDRelatedField(
        slug_field='uuid',
        queryset=get_user_model().objects.all())
    status = serializers.CharField()


class ApplicantSerializer(serializers.Serializer):
    user = UserUUIDRelatedField(
        slug_field='uuid',
        queryset=get_user_model().objects.all())
    summary = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    status = serializers.CharField()
    slot = serializers.DateTimeField(required=False)


class RatingSerializer(serializers.Serializer):
    user = UserUUIDRelatedField(
        slug_field='uuid',
        queryset=get_user_model().objects.all())
    rating = serializers.IntegerField()
    comment = serializers.CharField(
        required=False, allow_blank=True)


class MigrateTicketSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(
        queryset=OpportunityGroup.objects.all())
    keywords = KeywordSerializer(many=True, required=False)
    languages = LanguageSerializer(many=True, required=False)
    users_tagged = UserTaggedSerializer(
        required=False, many=True)
    status = serializers.CharField()
    history = HistorySerializer(many=True)
    applicants = ApplicantSerializer(many=True)
    created = serializers.DateTimeField(required=False)
    files = UploadedFileSerializer(required=False, many=True)
    ratings = RatingSerializer(required=False, many=True)

    class Meta:
        model = Opportunity
        fields = [
            'group', 'title', 'description',
            'keywords', 'deadline_date',
            'slug', 'mode', 'uuid', 'target',
            'users_tagged', 'created',
            'status', 'history', 'applicants',
            'files', 'ratings', 'languages',
        ]

    def create(self, validated_data):
        keywords = Keyword.objects.update_keywords(
            user_from=validated_data.get('user_from'),
            keywords_name=[k['name'] for k in validated_data.get('keywords')],
        )
        validated_data['keywords'] = keywords
        languages = Language.objects.update_languages(
            user_from=validated_data.get('user_from'),
            languages_name=set([k['name'] for k in validated_data.get('languages', [])]),
        )
        validated_data['languages'] = languages
        validated_data['users_tagged'] = [u['user'] for u in validated_data.get('users_tagged', [])]
        return create_opportunity_from_ticket(**validated_data)

    def to_representation(self, obj):
        return {'uuid': obj.uuid.__str__()}
