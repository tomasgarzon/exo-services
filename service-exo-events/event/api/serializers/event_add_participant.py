from rest_framework import serializers
from django.conf import settings

from exo_role.models import ExORole

from ...models import Participant, Event


class AddParticipantSerializer(serializers.ModelSerializer):

    uuid = serializers.UUIDField(
        format='hex_verbose',
        allow_null=True,
        required=False
    )
    full_name = serializers.CharField(required=False)
    user_email = serializers.EmailField(required=False)
    exo_role = serializers.SlugRelatedField(queryset=ExORole.objects.all(), slug_field='code')

    class Meta:
        model = Participant
        fields = [
            'id',
            'uuid',
            'full_name',
            'user_email',
            'exo_role',
        ]

    def create(self, validated_data):
        event = validated_data.pop('event')
        return event.add_participant(**validated_data)

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data.update({'full_name': obj.user_name})
        return data


class AddParticipantPublicSerializer(serializers.Serializer):
    name = serializers.CharField(source='user_name')
    email = serializers.EmailField(source='user_email')
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.filter_by_category(settings.EXO_ROLE_CATEGORY_SUMMIT),
    )

    class Meta:
        model = Participant
        fields = [
            'name',
            'email',
            'event_id',
        ]

    def create(self, validated_data):
        event = validated_data.get('event_id')
        name = validated_data.get('user_name')
        email = validated_data.get('user_email')
        return event.add_participant_public(name, email)


class UpdateParticipantSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(source='user_name', required=False)
    user_email = serializers.EmailField(required=False)

    class Meta:
        model = Participant
        fields = ['full_name', 'user_email']


class UploadParticipantSerializer(serializers.Serializer):
    content = serializers.CharField()
    exo_role = serializers.SlugRelatedField(
        queryset=ExORole.objects.all(),
        slug_field='code',
        allow_null=True,
        required=False,
    )

    class Meta:
        fields = ['content', 'exo_role']

    def create(self, validated_data):
        event = validated_data.get('event')
        data = validated_data.get('content')
        exo_role = validated_data.get('exo_role')
        user_list = data.splitlines()
        users = []

        for user in user_list:
            name, email = user.split(',')
            data = {
                'full_name': name,
                'user_email': email,
                'exo_role': exo_role,
            }
            participant = event.add_participant(**data)
            users.append(participant.pk)
        return event.participants.filter(id__in=users)
