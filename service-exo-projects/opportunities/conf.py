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


class OpportunitiesConfig(AppConf):
    APP_NAME = 'opportunities'

    DURATION_UNITY_MINUTE = 'T'
    DURATION_UNITY_HOUR = 'H'
    DURATION_UNITY_DAY = 'D'
    DURATION_UNITY_WEEK = 'W'
    DURATION_UNITY_MONTH = 'M'

    DURATION_UNITY_CHOICES = (
        (DURATION_UNITY_MINUTE, 'Minute'),
        (DURATION_UNITY_HOUR, 'Hour'),
        (DURATION_UNITY_DAY, 'Day'),
        (DURATION_UNITY_WEEK, 'Week'),
        (DURATION_UNITY_MONTH, 'Month'),
    )

    CH_CURRENCY_EUR = 'E'
    CH_CURRENCY_DOLLAR = 'D'
    CH_CURRENCY_EXOS = 'X'
