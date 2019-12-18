from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel


class Participant(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='participant',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return '{}-{}'.format(self.user, self.email)

    @property
    def uuid(self):
        return self.user.uuid

    @property
    def short_name(self):
        return self.name.split(' ')[0]

    @property
    def full_name(self):
        return self.name

    @property
    def profile_url(self):
        return ''

    @property
    def profile_picture(self):
        return []

    @property
    def user_title(self):
        return ''

    @property
    def slug(self):
        return ''
