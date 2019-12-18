from django.conf import settings
from django.db import models
from django.utils import timezone


class StripeIntentMixin(models.Model):

    intent_id = models.CharField(max_length=512, blank=True, null=True)
    intent_client_secret_id = models.CharField(
        max_length=512,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    @property
    def intent_description(self):
        return '{} for {}'.format(
            self.concept,
            self.full_name,
        )

    def payment_intent_success(self, payment_id):
        self._stripe_payment_id = payment_id
        self.date_payment = timezone.now()
        self.status = settings.PAYMENTS_CH_PAID
        self.save(update_fields=[
            'status',
            'date_payment',
            '_stripe_payment_id',
        ])

    def payment_intent_fail(self):
        self.status = settings.PAYMENTS_CH_ERROR
        self.save(update_fields=['status'])
