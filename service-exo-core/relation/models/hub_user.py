from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel

from ..managers.hub_user import HubUserManager


class HubUser(TimeStampedModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='hubs',
        on_delete=models.CASCADE)
    hub = models.ForeignKey(
        'exo_hub.ExOHub', related_name='users',
        on_delete=models.CASCADE)

    objects = HubUserManager()

    def __str__(self):
        return '{} - {}'.format(self.user, self.hub)
