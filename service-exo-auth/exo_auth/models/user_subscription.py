from model_utils.models import TimeStampedModel

from django.db import models


class UserSubscription(TimeStampedModel):
    user_uuid = models.UUIDField()
    subscription = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user_uuid', 'subscription')

    def __str__(self):
        return '{} - {}'.format(self.user_uuid, self.subscription)
