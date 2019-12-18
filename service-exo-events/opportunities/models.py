from django.db import models
from model_utils.models import TimeStampedModel


class OpportunityParticipant(TimeStampedModel):
    participant = models.OneToOneField(
        'event.Participant',
        related_name='opportunity_related',
        on_delete=models.CASCADE)
    opportunity_uuid = models.UUIDField()
