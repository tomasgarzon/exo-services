# -*- coding: utf-8 -*-
# Generated for Django 2.2.2 on 2019-06-11 18:42
from __future__ import unicode_literals

import stripe

from django.conf import settings

from exo_changelog import change, operations

from ..models import Payment


def update_pending_payments_to_new_api():
    log = open('{}.log'.format(__file__.split('.py')[0]), 'a')
    log.write('Stripe generated objects:\n')
    stripe.api_key = settings.STRIPE_SECRET_KEY
    for payment in Payment.objects.filter(
            status=settings.PAYMENTS_CH_PENDING,
            intent_id__isnull=True):
        stripe_intent_created = stripe.PaymentIntent.create(
            amount=payment.amount_normalized,
            currency=payment.currency,
            description=payment.intent_description,
            receipt_email=payment.email,
        )

        payment.intent_id = stripe_intent_created.get('id')
        payment.intent_client_secret_id = stripe_intent_created.get('client_secret')
        payment.save(update_fields=['intent_id', 'intent_client_secret_id'])
        log.write('StripePayment created for: {}\n'.format(payment))

    log.close()


class Change(change.Change):

    dependencies = [
    ]

    operations = [
        operations.RunPython(update_pending_payments_to_new_api)
    ]
