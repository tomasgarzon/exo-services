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


class ExOAttributesConfig(AppConf):
    APP_NAME = 'exo_attributes'

    CH_SCALE = 'S'
    CH_IDEAS = 'I'

    CH_EXO_TYPE = (
        (CH_SCALE, 'Scale'),
        (CH_IDEAS, 'Ideas'),
    )
