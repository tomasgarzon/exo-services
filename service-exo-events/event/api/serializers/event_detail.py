from rest_framework import serializers

from ...models import Event
from .organizer_serializer import OrganizerSerializer
from .mixins import EventMixinSerializer
from .participant_serializer import ParticipantSerializer


class EventDetailSerializer(EventMixinSerializer, serializers.ModelSerializer):

    category = serializers.CharField(source='category.code')
    organizers = OrganizerSerializer(many=True, read_only=True)
    is_free = serializers.SerializerMethodField()
    participants = ParticipantSerializer(many=True, source='speakers')

    class Meta:
        model = Event
        fields = [
            'uuid', 'trainer',
            'category', 'type_event_name',
            'follow_type', 'follow_type_name',
            'status',
            'title', 'sub_title', 'slug', 'event_image',
            'description',
            'start', 'end',
            'location', 'place_id',
            'url',
            'languages',
            'show_price', 'price', 'is_free',
            'organizers',
            'participants'
        ]

    def get_is_free(self, obj):
        return obj.amount == 0
