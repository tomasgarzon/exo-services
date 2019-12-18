from django.db import models

from model_utils.models import TimeStampedModel

from ...conf import settings


class PartnerProjectRole(TimeStampedModel):

    partner = models.ForeignKey(
        'partner.Partner',
        related_name='projects_roles',
        on_delete=models.CASCADE,
    )
    project = models.ForeignKey(
        'project.Project',
        related_name='partners_roles',
        on_delete=models.CASCADE,
    )

    status = models.CharField(
        max_length=1,
        choices=settings.RELATION_ROLE_CH_STATUS,
        default=settings.RELATION_ROLE_CH_INACTIVE,
    )
    visible = models.BooleanField(
        default=True)

    class Meta:
        verbose_name_plural = 'Partner Projects'
        verbose_name = 'Partner Project'
        unique_together = ('project', 'partner',)

    def __str__(self):
        return str('%s %s' % (self.partner, self.project))
