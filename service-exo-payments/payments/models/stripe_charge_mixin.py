from django.db import models


class StripeChargeMixin(models.Model):  # Deprecated

    _stripe_auth_token_code = models.CharField(
        max_length=256,
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True
