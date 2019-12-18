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
from django.utils.text import slugify

logger = logging.getLogger(__name__)


class RegistrationConfig(AppConf):
    APP_LABEL = 'registration'
    GROUP_NAME = 'registration'

    # Delete this
    LOGGABLE_STATUS = ['S', 'P', 'A', 'W']

    CH_CURRENT = 'A'
    CH_PENDING = 'P'
    CH_EXECUTED = 'X'
    CH_CANCEL = 'C'

    CH_STEP_STATUS_DEFAULT = CH_PENDING
    CH_STEP_STATUS_REACTIVATED = CH_PENDING
    CH_STEP_STATUS = (
        (CH_CURRENT, 'Current'),
        (CH_PENDING, 'Pending'),
        (CH_EXECUTED, 'Executed'),
        (CH_CANCEL, 'Declined'),
    )

    # ##
    # Process Options definitions
    # ##

    OPTION_SEND_ADMIN_EMAIL = 'send_admin_email_by_default'
    OPTION_SEND_USER_EMAIL = 'send_user_email_by_default'
    OPTION_PUBLIC_LOG_VIEW = 'public_log_view'

    STEP_AGREEMENT = 'Agreement'
    STEP_SKILL_ASSESSMENT = 'Skill Assessment'
    STEP_SIGNUP = 'Sign Up'
    STEP_PROFILE = 'Welcome Onboarding'

    STEPS_NAMES = (
        (slugify(STEP_AGREEMENT), STEP_AGREEMENT),
        (slugify(STEP_SKILL_ASSESSMENT), STEP_SKILL_ASSESSMENT),
        (slugify(STEP_SIGNUP), STEP_SIGNUP),
        (slugify(STEP_PROFILE), STEP_PROFILE),
    )
