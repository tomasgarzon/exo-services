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
from django.conf import settings  # NOQA

logger = logging.getLogger(__name__)


class ExoAuthConfig(AppConf):
    APP_NAME = 'exo-auth'

    VALIDATION_CHOICES_VERIFIED = 'V'
    VALIDATION_CHOICES_NOT_VERIFIED = 'NV'
    VALIDATION_CHOICES_NOT_OWNER = 'X'      # Is not the email owner
    VALIDATION_CHOICES_OTHER_USER = 'O'
    VALIDATION_CHOICES_PENDING = 'P'
    VALIDATION_CHOICES_DISCARTED = 'D'

    EMAIL_VALIDATION = {
        VALIDATION_CHOICES_VERIFIED: 'Email account changed successfully',
        VALIDATION_CHOICES_NOT_VERIFIED: 'You have already added this email '
        'before, but it wasn\'t verified yet. Please check your email inbox',
        VALIDATION_CHOICES_NOT_OWNER: 'Sorry, this email does not exist',
        VALIDATION_CHOICES_OTHER_USER: 'Sorry, there is an user with this email'
        ' address. Please contact to support@openexo.com for more details.',
        VALIDATION_CHOICES_PENDING: 'We have sent an email to validate'
        ' this email account. Please, have a look to your inbox. ',
        VALIDATION_CHOICES_DISCARTED: 'You email has been discarted'
    }

    PERMS_USER_EDIT = 'user_edit_profile'

    ALL_PERMISSIONS = (
        (PERMS_USER_EDIT, 'Edit User Profile'),
    )

    TOPIC_CONNECTED = 'connected'
    USER_CONNECTED = 'connected'
    USER_DISCONNECTED = 'disconnected'
