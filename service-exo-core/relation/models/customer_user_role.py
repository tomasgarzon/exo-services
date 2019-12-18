from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings
from ..managers.customer_user import CustomerUserRoleManager
from .position import UserPositionMixin


class CustomerUserRole(UserPositionMixin, TimeStampedModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='customers_roles',
        on_delete=models.CASCADE,
    )
    customer = models.ForeignKey(
        'customer.Customer',
        related_name='users_roles',
        on_delete=models.CASCADE,
    )

    status = models.CharField(
        max_length=1,
        choices=settings.RELATION_ROLE_CH_STATUS,
        default=settings.RELATION_ROLE_CH_INACTIVE,
    )
    visible = models.BooleanField(
        default=True)

    objects = CustomerUserRoleManager()

    _perms_activate = settings.CUSTOMER_ADD_USER
    _related_object = 'customer'

    class Meta:
        verbose_name_plural = 'Customer Users'
        verbose_name = 'Customer User'
        permissions = settings.RELATION_ALL_PERMISSIONS
        unique_together = ('user', 'customer',)

    def __str__(self):
        return str('%s %s' % (self.user, self.customer))

    def send_notification(self, invitation):
        return None

    @property
    def is_active(self):
        return self.status == settings.RELATION_ROLE_CH_ACTIVE
