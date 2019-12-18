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


class UtilsConfig(AppConf):
    APP_NAME = 'utils'

    # Stream types
    STREAM_CH_EDGE = 'E'
    STREAM_CH_CORE = 'C'
    STREAM_CH_UNIQUE = 'U'
    STREAM_CH_TYPE_DEFAULT = STREAM_CH_EDGE

    STREAM_CH_TYPE = (
        (STREAM_CH_EDGE, 'Edge Stream'),
        (STREAM_CH_CORE, 'Core Stream'),
        (STREAM_CH_UNIQUE, 'Unique'),
    )
