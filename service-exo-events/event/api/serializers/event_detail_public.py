from django.conf import settings

from rest_framework import serializers

from auth_uuid.utils.user_wrapper import UserWrapper

from ...models import Event
from .organizer_serializer import OrganizerSerializer
from .participant_serializer import ParticipantSerializer
from .mixins import EventMixinSerializer


class EventDetailPublicWebsiteSerializer(
        EventMixinSerializer,
        serializers.ModelSerializer):

    organizers = OrganizerSerializer(many=True, read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    name = serializers.CharField(source='title')
    country = serializers.SerializerMethodField()
    languages = serializers.SerializerMethodField()
    follow_type = serializers.SerializerMethodField()
    is_free = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'uuid', 'trainer',
            'category', 'type_event_name',
            'follow_type', 'follow_type_name',
            'status',
            'name', 'sub_title', 'slug', 'event_image',
            'description',
            'start', 'end',
            'location', 'place_id', 'country',
            'url',
            'languages',
            'price', 'is_free',
            'organizers',
            'participants',
        ]

    def get_country(self, obj):
        country = ''
        if obj.location:
            location = obj.location.split(',')
            if len(location) == 2:
                country = location[1]

        return country.strip()

    def get_languages(self, obj):
        return obj.languages[0] if obj.languages else ''

    def get_follow_type(self, obj):
        return obj.follow_type

    def get_is_free(self, obj):
        return obj.amount > 0


class EventPublicSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='title')
    comments = serializers.CharField(source='description')
    signUpApi = serializers.SerializerMethodField()
    trainer = serializers.SerializerMethodField()
    speakers = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'uuid',
            'name',
            'sub_title',
            'start',
            'end',
            'location',
            'trainer',
            'speakers',
            'comments',
            'signUpApi',
        ]

    def get_signUpApi(self, obj):
        return ''

    def get_trainer(self, obj):
        user_data = obj.main_speaker_data
        return {
            'username': user_data.get('fullName'),
            'email': user_data.get('email'),
            'profile_url': user_data.get('profileUrl'),
            'picture': user_data.get('profilePicture'),
        }

    def get_speakers(self, obj):
        data = []
        speakers = obj.participants.filter_by_role_name(settings.EVENT_SPEAKER_NAME)
        for participant in speakers:
            user_wrapper = UserWrapper(user=participant.user)
            value = {
                'name': user_wrapper.get_full_name(),
                'profile_url': '{}{}'.format(
                    settings.DOMAIN_NAME,
                    user_wrapper.profile_url,
                ),
                'bio': user_wrapper.bio_me,
                'linkedin': user_wrapper.linkedin,
                'profile_picture': user_wrapper.profile_picture_96,
                'title': user_wrapper.user_title
            }
            data.append(value)
        return data
