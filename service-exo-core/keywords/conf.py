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


class KeywordsConfig(AppConf):
    APP_NAME = 'keywords'

    CH_PROFILE = 'profile'
    CH_TICKET = 'ticket'
    CH_TECHNOLOGY = 'technology'
    CH_EXPERTISE = 'expertise'
    CH_INDUSTRY = 'industry'
