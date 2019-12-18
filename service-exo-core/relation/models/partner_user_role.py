from django.db import models

from model_utils.models import TimeStampedModel

from ..managers.partner_user import PartnerUserRoleManager
from ..conf import settings
from .position import UserPositionMixin


class PartnerUserRole(UserPositionMixin, TimeStampedModel):

    partner = models.ForeignKey(
        'partner.Partner',
        related_name='users_roles',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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

    objects = PartnerUserRoleManager()
    _perms_activate = settings.PARTNER_ADD_USER
    _related_object = 'partner'

    class Meta:
        verbose_name_plural = 'Partner Users'
        verbose_name = 'Partner User'
        permissions = settings.RELATION_ALL_PERMISSIONS
        unique_together = ('user', 'partner')

    def __str__(self):
        return str('%s %s' % (
            self.user, self.partner
        ))

    def send_notification(self, invitation):
        return None
