from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel


class CouponLog(TimeStampedModel):
    coupon = models.ForeignKey(
        'Coupon',
        on_delete=models.CASCADE,
        related_name='logs')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)

    def __str__(self):
        return self.coupon
