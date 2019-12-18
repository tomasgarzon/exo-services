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


class InvitationConfig(AppConf):

    APP_LABEL = 'invitation'

    STATUS_CH_ACTIVE = 'A'
    STATUS_CH_PENDING = 'P'
    STATUS_CH_CANCELLED = 'C'

    CH_STATUS = (
        (STATUS_CH_ACTIVE, 'Active'),
        (STATUS_CH_PENDING, 'Pending'),
        (STATUS_CH_CANCELLED, 'Cancelled'),
    )

    TYPE_ROLES = 'R'
    TYPE_AGREEMENT = 'G'
    TYPE_SKILLS = 'S'
    TYPE_TEST = 'T'
    TYPE_APPLICATION = 'A'
    TYPE_TEAM = 'E'
    TYPE_SIGNUP = 'U'
    TYPE_SIMPLE_SIGNUP = 'X'
    TYPE_SURVEY = 'V'
    TYPE_PROFILE = 'F'
    TYPE_TICKET = 'K'

    CH_TYPE = (
        (TYPE_ROLES, 'Roles'),
        (TYPE_SKILLS, 'Skills'),
        (TYPE_TEST, 'Test'),
        (TYPE_APPLICATION, 'Application'),
        (TYPE_AGREEMENT, 'Agreement'),
        (TYPE_PROFILE, 'On boarding'),
        (TYPE_TEAM, 'Team'),
        (TYPE_SIGNUP, 'Signup'),
        (TYPE_SIMPLE_SIGNUP, 'Simple SignUp'),
        (TYPE_SURVEY, 'Survey'),
        (TYPE_TICKET, 'Ticket'),
    )

    CH_TYPE_LOG_STATUS = 'S'
    CH_TYPE_LOG_SEND = 'D'

    CH_TYPE_LOG = (
        (CH_TYPE_LOG_STATUS, 'Status changed'),
        (CH_TYPE_LOG_SEND, 'Notification Sent'),
    )

    CH_TYPE_LOG_DEFAULT = CH_TYPE_LOG_STATUS

    # ##
    # Permissions
    # ##
    ACCEPT = 'accept_invitation'
    CANCEL = 'cancel_invitation'
    RESEND = 'resend_invitation'

    ALL_PERMISSIONS = (
        (ACCEPT, 'Can accept the invitation'),
        (CANCEL, 'Can cancel/deny the invitation'),
        (RESEND, 'Can resend the invitation'),
    )

    FULL_ACCEPT = '{}.{}'.format(APP_LABEL, ACCEPT)
    FULL_CANCEL = '{}.{}'.format(APP_LABEL, CANCEL)
    FULL_RESEND = '{}.{}'.format(APP_LABEL, RESEND)
