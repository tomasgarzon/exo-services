from django.db import models
from django.db.models import ForeignKey

from model_utils.models import TimeStampedModel

from ..conf import settings


class MessageLog(TimeStampedModel):
    message = models.TextField(default=None, blank=True, null=True)
    action = models.CharField(
        max_length=1,
        choices=settings.MAIL_LOG_ACTIONS_CHOICES,
        default=settings.MAIL_LOG_ACTIONS_DEFAULT)
    email = ForeignKey(
        to='mail.Message',
        related_name='log',
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'MessageLog'
        verbose_name_plural = 'MessageLogs'

    def __str__(self):
        return '[{}] {}: {}'.format(
            self.created,
            self.get_action_display(),
            self.email.subject)

    @property
    def subject(self):
        if self.email is not None:
            return self.email.subject
        else:
            return None
