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


class AchievementConfig(AppConf):
    APP_NAME = 'achievement'

    # Consultant Status
    STATUS_CH_COMPLETED = 'C'
    STATUS_CH_PENDING = 'P'
    STATUS_DEFAULT = STATUS_CH_PENDING
    STATUS_CH_STATUS = (
        (STATUS_CH_COMPLETED, 'Completed'),
        (STATUS_CH_PENDING, 'Pending'),
    )

    CH_CODE_FILL_PROFILE = 'F'
    CH_CODE = (
        (CH_CODE_FILL_PROFILE, 'Fill profile'),
    )

    REWARD_CH_CODE_COIN = 'C'
    REWARD_CH_CODE = (
        (REWARD_CH_CODE_COIN, 'Coins'),
    )

    KEYWORDS_FOR_UNLOCK = 10
