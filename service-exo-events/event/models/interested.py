from django.db import models

from model_utils.models import TimeStampedModel


class Interested(TimeStampedModel):
    event = models.ForeignKey(
        'Event',
        related_name='interested',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255)

    def __str__(self):
        return self.email
