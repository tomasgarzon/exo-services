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


class ExOAreaConfig(AppConf):
    APP_NAME = 'exo_area'

    CH_AREA_ORGANIZATION = 'O'
    CH_AREA_INSTITUTION = 'I'
    CH_AREA_PEOPLE = 'P'

    CH_EXO_AREAS_NAMES = (
        (CH_AREA_ORGANIZATION, 'Organizations'),
        (CH_AREA_INSTITUTION, 'Institutions'),
        (CH_AREA_PEOPLE, 'Peoples'),
    )

    CH_EXO_AREAS_CODE = (
        (CH_AREA_ORGANIZATION, 'organization'),
        (CH_AREA_INSTITUTION, 'institution'),
        (CH_AREA_PEOPLE, 'people'),
    )
