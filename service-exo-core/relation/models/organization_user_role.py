from django.db import models

from model_utils.models import TimeStampedModel

from .position import UserPositionMixin
from ..conf import settings


class OrganizationUserRole(UserPositionMixin, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='organizations_roles',
        on_delete=models.CASCADE
    )
    organization = models.ForeignKey(
        'custom_auth.InternalOrganization',
        related_name='users_roles',
        on_delete=models.CASCADE
    )
    position = models.CharField(
        max_length=200, blank=True, null=True)

    status = models.CharField(
        max_length=1,
        choices=settings.RELATION_ROLE_CH_STATUS,
        default=settings.RELATION_ROLE_CH_INACTIVE,
    )
    visible = models.BooleanField(
        default=True)

    class Meta:
        verbose_name_plural = 'Internal Organization Users'
        verbose_name = 'Internal Organization User'
        unique_together = ('user', 'organization',)
        permissions = settings.RELATION_ALL_PERMISSIONS

    def __str__(self):
        return '{} {}'.format(self.user, self.organization)

    def send_notification(self, invitation):
        return None

    @property
    def is_active(self):
        return self.status == settings.RELATION_ROLE_CH_ACTIVE
