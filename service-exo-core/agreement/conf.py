# -*- coding: utf-8 -*-

"""
License boilerplate should be used here.
"""

# python 3 imports
from __future__ import absolute_import, unicode_literals

# python imports
import logging

# 3rd. libraries imports
from appconf import AppConf

# django imports
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class AgreementConfig(AppConf):

    # Agreeemen status
    STATUS_ACTIVE = 'A'
    STATUS_INACTIVE = 'I'
    STATUS_CANCELLED = 'C'

    STATUS_DEFAULT = STATUS_INACTIVE

    STATUS = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    # Agreements User status
    USER_STATUS_SIGNED = 'S'
    USER_STATUS_PENDING = 'P'
    USER_STATUS_REVOKED = 'I'

    USER_STATUS_DEFAULT = USER_STATUS_PENDING

    USER_STATUS = (
        (USER_STATUS_SIGNED, 'Accepted'),
        (USER_STATUS_PENDING, 'Pending'),
        (USER_STATUS_REVOKED, 'Revoked'),
    )

    # Agreement receipts
    RECIPIENT_GENERAL = 'G'
    RECIPIENT_CONSULTANT = 'C'
    RECIPIENT_REGULAR_USER = 'U'

    RECIPIENT_DEFAULT = RECIPIENT_GENERAL

    RECIPIENT = (
        (RECIPIENT_GENERAL, 'General'),
        (RECIPIENT_CONSULTANT, 'Consultants'),
        (RECIPIENT_REGULAR_USER, 'Regular Users'),
    )

    TEMPLATE_FOLDER = 'agreement'

    PDF_PREFIX = 'OpenExO Agreement v'

    DOMAIN_CH_TOS = 'T'
    DOMAIN_CH_ACTIVITY = 'A'
    DOMAIN_CH_MARKETPLACE = 'M'
    DOMAIN_CH_EXQ = 'E'
    DOMAIN_DEFAULT = DOMAIN_CH_TOS

    DOMAIN_CHOICES = (
        (DOMAIN_CH_TOS, 'Terms of service'),
        (DOMAIN_CH_ACTIVITY, 'Activity'),
        (DOMAIN_CH_MARKETPLACE, 'Marketplace'),
        (DOMAIN_CH_EXQ, 'ExQ'),
    )
