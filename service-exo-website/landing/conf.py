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


class LandingConfig(AppConf):

    CH_FORTY = 'forty'
    CH_STELLAR = 'stellar'

    CH_THEME_DEFAULT = CH_STELLAR
    CH_THEMES = (
        (CH_FORTY, 'Forty'),
        (CH_STELLAR, 'Stellar'),
    )

    CH_WORKSHOP = 'workshop'
    CH_EVENT = 'event'

    CH_TYPE_DEFAULT = CH_WORKSHOP
    CH_PAGE_TYPES = (
        (CH_WORKSHOP, 'Workshop'),
        (CH_EVENT, 'Event'),
    )
