from rest_framework import serializers

from exo_role.models import Category

from ...models import Event
from ...helpers import EventPermissionHelper
from .organizer_serializer import OrganizerSerializer
from .participant_serializer import ParticipantSerializer
from .mixins import EventMixinSerializer


class EventSerializer(EventMixinSerializer, serializers.ModelSerializer):

    category = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='code')
    uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    organizers = OrganizerSerializer(many=True, required=False)
    participants = ParticipantSerializer(many=True)
    is_free = serializers.SerializerMethodField()
    type_event_name = serializers.CharField(source='type_event_other', required=False, allow_blank=True)
    event_image = serializers.CharField(source='url_image', required=False, allow_blank=True)

    class Meta:
        model = Event
        read_only_fields = [
            'uuid', 'trainer', 'follow_type_name', 'is_free']
        fields = [
            'uuid',
            'category', 'type_event_name',
            'follow_type', 'follow_type_name',
            'status',
            'title', 'sub_title', 'slug', 'event_image',
            'description',
            'start', 'end',
            'location', 'place_id',
            'url',
            'languages',
            'show_price',
            'amount', 'is_free',
            'currency',
            'organizers',
            'participants'
        ]

    def validate_category(self, value):
        user = self.context.get('view').request.user
        helper = EventPermissionHelper()
        try:
            assert helper.has_perm(user, 'create_{}'.format(value.code))
        except AssertionError:
            raise serializers.ValidationError('You are not able to create this Event')

        return value

    def create(self, validated_data):
        return Event.objects.create_event(**validated_data)

    def update(self, instance, validated_data):
        organizers_data = validated_data.pop('organizers', [])
        participants_data = validated_data.pop('participants', [])

        instance = super().update(instance, validated_data)
        instance.update_organizers(organizers_data)
        instance.update_participants(participants_data)

        return instance

    def get_is_free(self, obj):
        return obj.amount == 0
