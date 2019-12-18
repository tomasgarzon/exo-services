from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings


class ConversationUser(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='conversations',
        on_delete=models.CASCADE)
    conversation = models.ForeignKey(
        'Conversation',
        related_name='users',
        on_delete=models.CASCADE)
    name = models.CharField(
        max_length=200,
        null=True)
    profile_picture = models.CharField(
        null=True, blank=True,
        max_length=200)
    short_title = models.CharField(
        max_length=200,
        null=True, blank=True)
    profile_url = models.CharField(
        default='',
        max_length=200,
        null=True, blank=True)

    @property
    def uuid(self):
        return str(self.user.uuid)

    @property
    def slug(self):
        if self.profile_url is None:
            return ''
        return self.profile_url.split('/')[-2] if self.profile_url.endswith('/') else self.profile_url.split('/')[-1]
