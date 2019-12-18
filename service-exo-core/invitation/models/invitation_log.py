from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings


class InvitationLog(TimeStampedModel):
    invitation = models.ForeignKey(
        'Invitation', related_name='logs',
        on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    log_type = models.CharField(
        max_length=1,
        choices=settings.INVITATION_CH_TYPE_LOG,
        default=settings.INVITATION_CH_TYPE_LOG_DEFAULT,
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return '{} {}'.format(self.invitation, self.get_log_type_display())
