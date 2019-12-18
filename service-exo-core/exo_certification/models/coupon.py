from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.utils import timezone

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin


class Coupon(CreatedByMixin, TimeStampedModel):
    code = models.CharField(unique=True, max_length=20)
    certification = models.ForeignKey(
        'ExOCertification',
        blank=False, null=True,
        related_name='coupons',
        on_delete=models.CASCADE,
    )
    expiry_date = models.DateTimeField(blank=True, null=True)
    max_uses = models.IntegerField(default=10)
    uses = models.IntegerField(default=0)
    discount = models.FloatField(default=0)
    type = models.CharField(
        max_length=1,
        choices=settings.EXO_CERTIFICATION_COUPON_CH_TYPES,
        default=settings.EXO_CERTIFICATION_COUPON_TYPES_CH_DEFAULT,
    )
    owner = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        related_name='referral_codes',
        on_delete=models.CASCADE,
    )
    fixed_email = models.EmailField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.code

    def apply(self, user, raise_exceptions=True):
        if self.is_available:
            self.uses = F('uses') + 1
            self.save(update_fields=['uses'])
            self.refresh_from_db()
            self.create_log(user)
            return True
        elif raise_exceptions:
            raise PermissionError
        else:
            return False

    def can_use_coupon(self, certification, raise_exceptions=True):
        is_valid = False
        if self.is_available and self.certification == certification:
            is_valid = True
        if raise_exceptions and not is_valid:
            raise PermissionError
        else:
            return is_valid

    @property
    def level(self):
        return self.certification.level

    @property
    def is_available(self):
        expired = False
        if self.expiry_date:
            expired = self.expiry_date < timezone.now()
        can_use = self.max_uses == 0 or self.max_uses > self.uses
        return not expired and can_use

    def check_for_user(self, user):
        if not self.fixed_email:
            return True
        return self.fixed_email == user.email

    def create_log(self, user):
        self.logs.create(user=user)

    @property
    def total_discount(self):
        if self.type == settings.EXO_CERTIFICATION_COUPON_TYPES_CH_PERCENT:
            return '{} %'.format(self.discount)
        return '{} $'.format(self.discount)
