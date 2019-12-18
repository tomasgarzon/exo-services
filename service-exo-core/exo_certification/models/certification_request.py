import logging

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models

from model_utils.models import TimeStampedModel

from referral.models import Campaign

from ..conf import settings
from ..signals_define import (
    certification_request_payment_success,
    certification_request_status_updated,
)
from .certification_metric_mixin import CertificationRequestMetricMixin

logger = logging.getLogger('referral')


class CertificationRequest(CertificationRequestMetricMixin, TimeStampedModel):
    user = models.ForeignKey(
        get_user_model(),
        related_name='certification_request',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    certification = models.ForeignKey(
        'exo_certification.ExOCertification',
        related_name='certification_requests',
        on_delete=models.CASCADE,
        blank=False,
        null=True,
    )
    payment_uuid = models.CharField(max_length=50, null=True, blank=True)
    payment_url = models.TextField(null=True, blank=True)
    coupon = models.ForeignKey(
        'Coupon',
        blank=True,
        null=True,
        related_name='certification_requests',
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=1,
        choices=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_STATUSES,
        default=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_DEFAULT,
    )

    cohort = models.ForeignKey(
        'exo_certification.CertificationCohort',
        related_name='certification_requests',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    price = models.FloatField(
        null=True,
        blank=True
    )
    application_details = JSONField(blank=True, null=True)
    requester_name = models.CharField(max_length=255, blank=True, null=True)
    requester_email = models.CharField(max_length=200, blank=True, null=True)
    hubspot_deal = models.CharField(max_length=200, blank=True, null=True)
    referrer = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Certification Request'
        verbose_name_plural = 'Certification Requests'

    def __str__(self):
        return '[{}] {} <{}> - {}'.format(
            self.created,
            self.requester_name,
            self.requester_email,
            self.get_status_display()
        )

    @property
    def level(self):
        return self.certification.level

    def update_price_with_coupon(self, coupon):
        price = self.cohort.price
        if coupon.type == settings.EXO_CERTIFICATION_COUPON_TYPES_CH_PERCENT:
            price = price - price * coupon.discount * 0.01
        else:
            price = price - coupon.discount
        return price

    def apply_coupon(self, coupon, user):
        price = self.update_price_with_coupon(coupon)
        price_is_valid = price >= 0
        if price_is_valid:
            coupon.apply(user)
            self.coupon = coupon
            self.price = price
            self.save()

    def validate_payment(self, payment_status):
        self.status = payment_status
        self.save(update_fields=['status'])
        if self.status == settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED:
            certification_request_payment_success.send(
                sender=self.__class__, pk=self.pk)

    def acquire_certificate(self, consultant_role):
        self.status = settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_FINISHED
        self.save(update_fields=['status'])
        self.report_acquire_action()

    def notify_referrer(self, conversion=False):
        if self.referrer:
            try:
                referrer = self.referrer.split(':')
                rh = referrer[0]
                campaign_id = referrer[1]
                campaign = Campaign.objects.get(campaign_id=campaign_id)
                campaign.subscribe(self.user, rh, conversion)
            except get_user_model().DoesNotExist:
                logger.info(
                    '[ERROR] CertificationRequest.notify_referrer(): User does not exist for CertificationRequest {}'.format(self.pk)  # noqa
                )
            except Campaign.DoesNotExist:
                logger.error(
                    'CertificationRequest.notify_referrer(): Campaign does not exist with id {}'.format(campaign_id)
                )
            except (IndexError, TypeError):
                logger.info(
                    '[ERROR] CertificationRequest.notify_referrer(): Malformed referrer for CertificationRequest {}'.format(  # noqa
                        self.referrer, self.pk)
                )

    def save(self, *args, **kwargs):
        is_new = True if not self.pk else False
        original = type(self).objects.get(pk=self.pk) if self.pk else None
        super().save(*args, **kwargs)
        if is_new or original and original.status != self.status:
            certification_request_status_updated.send(
                sender=self.__class__,
                pk=self.pk,
            )
