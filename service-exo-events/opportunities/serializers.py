from django.contrib.auth import get_user_model

from rest_framework import serializers
from exo_role.models import ExORole
from auth_uuid.utils.user_wrapper import UserWrapper

from utils.drf.relations import UserUUIDRelatedField
from event.models import Participant
from jobs.models import Job

from .models import OpportunityParticipant


class AddParticipantFromOpportunitySerializer(serializers.Serializer):
    user = UserUUIDRelatedField(
        slug_field='uuid',
        queryset=get_user_model().objects.all())
    exo_role = serializers.SlugRelatedField(
        slug_field='code',
        queryset=ExORole.objects.all())
    opportunity_uuid = serializers.UUIDField()
    user_from = UserUUIDRelatedField(
        slug_field='uuid',
        queryset=get_user_model().objects.all())

    def create(self, validated_data):
        event = validated_data.get('event')
        user_wrapper = UserWrapper(user=validated_data.get('user'))
        instance = Participant.objects.create(
            event=event,
            created_by=validated_data.get('user_from'),
            user=validated_data.get('user'),
            exo_role=validated_data.get('exo_role'),
            order=event.participants.count(),
            user_name=user_wrapper.get_full_name(),
            user_email=user_wrapper.email,
        )
        OpportunityParticipant.objects.create(
            participant=instance,
            opportunity_uuid=validated_data.get('opportunity_uuid'))
        job = instance.job
        job.delete()
        Job.objects.update_or_create(participant=instance)
        return instance
