# -*- coding: utf-8 -*-
# Generated for Django 2.2.5 on 2019-09-23 09:16
from __future__ import unicode_literals

import stripe
from django.conf import settings
from exo_changelog import change, operations

from payments.models import Payment


def cancel_useless_payment_intents():
    if not settings.POPULATOR_MODE:
        succeded = 0
        errored = 0
        print('Cancelling invalid payment intents on stripe')
        payments = Payment.objects.filter(
            status__in=settings.PAYMENTS_VALID_STATUS_UPDATE,
            _type=settings.PAYMENTS_TYPE_CERTIFICATION,
            intent_id__isnull=False,
        )
        print('Found {} items!'.format(payments.count()))

        stripe.api_key = settings.STRIPE_SECRET_KEY

        for p in payments:
            try:
                stripe.PaymentIntent.cancel(
                    p.intent_id, cancellation_reason='duplicate')
                print('Intent {} cancelled'.format(p.intent_id))
                succeded += 1

            except stripe.error.InvalidRequestError as exc:
                print('ERROR: {}'.format(exc))
                errored += 1

        print('Succesfully updated {} items'.format(succeded))
        print('Found {} errors'.format(errored))


class Change(change.Change):

    dependencies = [
        ('payments', '0002_auto_20190919_1410'),
    ]

    operations = [
        operations.RunPython(cancel_useless_payment_intents)
    ]
