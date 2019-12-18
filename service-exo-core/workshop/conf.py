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


class WorkshopConfig(AppConf):
    APP_NAME = 'workshop'

    DURATION_DAYS = 3

    PERMS_ADD_WORKSHOP = 'add_workshop'
    FULL_PERMS_ADD_WORKSHOP = '{}.{}'.format(
        APP_NAME, PERMS_ADD_WORKSHOP)
