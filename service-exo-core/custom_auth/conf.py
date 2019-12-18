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


class CustomAuthConfig(AppConf):
    APP_NAME = 'custom_auth'
    ADMIN_ROLE = 'admin_internal_organization'
    REGULAR_ROLE = 'regular_internal_organization'

    ALL_PERMISSIONS = (
        (ADMIN_ROLE, 'Admin role in organization'),
        (REGULAR_ROLE, 'Regular role in organization'),
    )

    USER_TOPIC = 'user'
