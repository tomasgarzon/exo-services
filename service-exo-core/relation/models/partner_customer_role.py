from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings


class PartnerCustomerRole(TimeStampedModel):

    partner = models.ForeignKey(
        'partner.Partner',
        related_name='customer_roles',
        on_delete=models.CASCADE,
    )
    customer = models.ForeignKey(
        'customer.Customer',
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
        verbose_name_plural = 'Partner Customers'
        verbose_name = 'Partner Customer'
        permissions = settings.RELATION_ALL_PERMISSIONS
        unique_together = ('customer', 'partner',)

    def __str__(self):
        return str('%s %s' % (self.customer, self.partner))

    def send_notification(self, invitation):
        return None
