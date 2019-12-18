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


class LearningConfig(AppConf):
    APP_NAME = 'learning'

    USER_MICROLEARNING_TYPEFORM_PARAM = 'object_id'
    USER_MICROLEARNING_STATUS_NONE = 'N'
    USER_MICROLEARNING_STATUS_PENDING = 'P'
    USER_MICROLEARNING_STATUS_DONE = 'D'

    USER_MICROLEARNING_STATUS_CHOICES = (
        (USER_MICROLEARNING_STATUS_NONE, 'Not available'),
        (USER_MICROLEARNING_STATUS_PENDING, 'Pending'),
        (USER_MICROLEARNING_STATUS_DONE, 'Done'),
    )

    VIDEO_DEFAULT_WIDTH = '100%'
    VIDEO_DEFAULT_HEIGHT = '100%'
