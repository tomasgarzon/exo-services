from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import serializers

from exo_role.models import ExORole

from ...models.participant import Participant


class FilteredListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.exclude(status=settings.EVENT_CH_ROLE_STATUS_DELETED)
        return super(FilteredListSerializer, self).to_representation(data)


class ParticipantSerializer(serializers.ModelSerializer):

    uuid = serializers.UUIDField(
        format='hex_verbose',
        source='user.uuid',
        allow_null=True,
        required=False,
    )

    full_name = serializers.CharField(source='user_name', required=False)
    user_email = serializers.EmailField(required=False)
    user_title = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    exo_role = serializers.SlugRelatedField(
        queryset=ExORole.objects.all(),
        slug_field='code',
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Participant
        list_serializer_class = FilteredListSerializer
        read_only_fields = ['status', 'role_name', 'user_title', 'id']
        fields = [
            'id',
            'uuid',
            'full_name', 'user_email',
            'user_title', 'thumbnail',
            'order',
            'exo_role', 'role_name',
            'status'
        ]

    def get_role_name(self, obj):
        return obj.participant_role_name

    def _is_user_retrieved(self, obj):
        is_current_user = False
        already_retrieved = hasattr(self, '_user_retrieved')
        if already_retrieved:
            is_current_user = self._user_retrieved == obj.user
        return already_retrieved and is_current_user

    def _retrieve_user_data(self, obj):
        if obj.user and obj.is_speaker:
            self._user_retrieved = obj.user
            self._user_data_retrieved = get_user_model().objects.retrieve_remote_user_data_by_uuid(
                obj.user.uuid
            )
            return self._user_retrieved

    def get_user_title(self, obj):
        user_title = ''
        if not self._is_user_retrieved(obj):
            self._retrieve_user_data(obj)
        if hasattr(self, '_user_data_retrieved') and self._user_data_retrieved:
            user_title = self._user_data_retrieved.get('userTitle')

        return user_title

    def get_thumbnail(self, obj):
        thumbnail = ''
        if not self._is_user_retrieved(obj):
            self._retrieve_user_data(obj)
        if hasattr(self, '_user_data_retrieved'):
            thumbnail = [value for key, value in self._user_data_retrieved.get('profilePicture') if key[0] == 144][0]

        return thumbnail

    def validate(self, attrs):
        uuid = attrs.get('user', {}).get('uuid')
        if not uuid:
            try:
                assert attrs.get('user_name', None)
                assert attrs.get('user_email', None)
            except AssertionError:
                raise ValidationError(
                    'You must define almost Oranizer UUID or Organizer complete \
                    information'
                )

        return attrs


class ParticipantBadgeListSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='exo_role.code')
    category = serializers.CharField(source='event.category.code')
    event_name = serializers.CharField(source='event.title')
    event_date = serializers.CharField(source='event.start')
    uuid = serializers.UUIDField(format='hex_verbose', source='user.uuid')

    class Meta:
        model = Participant
        fields = [
            'code',
            'category',
            'event_name',
            'event_date',
            'uuid',
        ]
