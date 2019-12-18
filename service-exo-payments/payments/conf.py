# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os

import logging

from appconf import AppConf

from django.conf import settings  # NOQA

logger = logging.getLogger(__name__)


class PaymentsConfig(AppConf):
    APP_NAME = 'payments'

    PAYMENT_TASK_DELAY_SECONDS = os.environ.get('PAYMENT_TASK_DELAY_SECONDS', 300)

    # Status for Payment

    CH_RECEIVED = 'S'
    CH_PENDING = 'P'
    CH_ERROR = 'X'
    CH_CANCELED = 'C'
    CH_ERASED = 'E'
    CH_PAID = 'A'
    CH_VALIDATED = 'V'

    VALID_STATUS_UPDATE = [CH_RECEIVED, CH_PENDING, CH_ERROR]

    REDIRECT_AFTER_PAYMENT_SUCCESS = 'https://www.openexo.com/payment-thank-you-page'
    REDIRECT_AFTER_PAYMENT_CANCEL = 'https://www.openexo.com/'

    PAYMENT_STATUS = (
        (CH_RECEIVED, 'Synchronizing'),
        (CH_PENDING, 'Pending'),
        (CH_ERROR, 'Error'),
        (CH_CANCELED, 'Canceled'),
        (CH_ERASED, 'Removed'),
        (CH_PAID, 'Paid'),
        (CH_VALIDATED, 'Verified'),
    )

    METHDO_CARD = 'Card'
    CH_ALTERNATIVE_PAYMENT_TOKENS = 'T'
    CH_ALTERNATIVE_PAYMENT_BANK_TRANSFER = 'B'
    ALTERNATIVE_PAYMENT = (
        (CH_ALTERNATIVE_PAYMENT_TOKENS, 'Tokens'),
        (CH_ALTERNATIVE_PAYMENT_BANK_TRANSFER, 'Bank transfer'),
    )

    CH_EUR = 'eur'
    CH_USD = 'usd'
    PAYMENT_CURRENCY = (
        (CH_EUR, 'EUR'),
        (CH_USD, 'USD'),
    )

    STRIPE_RESPONSE_STATUS_FIELD = 'status'
    STRIPE_RESPONSE_STATUS_OK = 'succeeded'

    PDF_DECODE_ISO = 'iso-8859-1'

    STRIPE_PAYMENT_INTENT_WEBHOOK_TYPE_SUCCESS = 'payment_intent.succeeded'
    STRIPE_PAYMENT_INTENT_WEBHOOK_TYPE_ERROR = 'payment_intent.payment_failed'

    # Invoice templates

    SPAIN_INVOICE = 'spain'
    EUROPE_INVOICE = 'europe'
    EXTRA_COMMUNITY_INVOICE = 'extra_community'
    INVOICE_PAYMENT_CHOICES = (
        (EUROPE_INVOICE, 'European Invoice'),
        (SPAIN_INVOICE, 'Spain Invoice'),
        (EXTRA_COMMUNITY_INVOICE, 'Extra Community Invoice'),
    )

    COUNTRY_SPAIN = 'ES'
    INVOICE_COUNTRY_RELATION = {
        SPAIN_INVOICE: [COUNTRY_SPAIN],
        EUROPE_INVOICE: [
            'AT', 'BE', 'BG', 'CY', 'CZ', 'HR', 'DK', 'EE', 'FI', 'FR', 'DE',
            'GR', 'HU', 'IS', 'IE', 'IT', 'LI', 'LV', 'LT', 'LU', 'MT', 'NL',
            'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'SE', 'GB',
        ],
    }

    # Payments type - CONCEPTS

    TYPE_CERTIFICATION = 'C'

    TYPE_CHOICES = (
        (TYPE_CERTIFICATION, 'Certification'),
    )

    CERTIFICATIONS_INVOICE_CODE = TYPE_CERTIFICATION    # C190001

    INVOICE_ID_CHOICE = (
        (TYPE_CERTIFICATION, 'C'),
    )

    VAT_DEFAULT = 21
    CERTIFICATION_PREFIX = 'C'
