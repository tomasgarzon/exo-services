from rest_framework import serializers

from ...models import Event
from .mixins import EventMixinSerializer
from .organizer_serializer import OrganizerSerializer
from .participant_serializer import ParticipantSerializer


class EventListSerializer(EventMixinSerializer, serializers.ModelSerializer):

    organizers = OrganizerSerializer(many=True, read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    is_free = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'uuid',
            'category', 'type_event_name',
            'follow_type', 'follow_type_name',
            'status',
            'title', 'sub_title', 'slug', 'event_image',
            'description',
            'start', 'end',
            'location', 'place_id', 'country',
            'url',
            'languages',
            'show_price', 'price', 'is_free',
            'participants',
            'organizers',
        ]

    def get_is_free(self, obj):
        return obj.amount == 0
