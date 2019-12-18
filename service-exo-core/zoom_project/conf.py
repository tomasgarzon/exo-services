# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""

# python 3 imports
from __future__ import absolute_import, unicode_literals

# python imports
import logging
import os

# 3rd. libraries imports
from appconf import AppConf

# django imports
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class ZoomProjectConfig(AppConf):

    # Join url example: https://zoom.us/j/123456789
    JOIN_URL = 'https://zoom.us/j'

    # Start url example: https://zoom.us/s/123456789?zak=hs65q23kd9sqliy612h23k
    START_URL = 'https://zoom.us/s'

    CH_STARTED = 'STARTED'
    CH_ENDED = 'ENDED'

    MEETING_STATUS = (
        (CH_STARTED, 'Started'),
        (CH_ENDED, 'Ended'),
    )

    API_KEY = os.environ.get('ZOOM_API_KEY', '')
    API_SECRET = os.environ.get('ZOOM_API_SECRET', '')
    TOKEN_NAME = 'zak'

    RETRY = 30
