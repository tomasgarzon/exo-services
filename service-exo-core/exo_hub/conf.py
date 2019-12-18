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


class ExOHubConfig(AppConf):
    APP_NAME = 'exo_hub'

    CH_COACH = 'C'
    CH_CONSULTANT = 'T'
    CH_ALUMNI = 'A'
    CH_AMBASSADORS = 'B'
    CH_TRAINER = 'R'
    CH_INVESTOR = 'I'

    CH_EXO_TYPE = (
        (CH_COACH, 'Coach'),
        (CH_CONSULTANT, 'Consultant'),
        (CH_ALUMNI, 'Alumni'),
        (CH_AMBASSADORS, 'Ambassador'),
        (CH_TRAINER, 'Trainer'),
        (CH_INVESTOR, 'Investor')
    )

    CIRCLES_NAMES = (
        (CH_COACH, 'Coaches'),
        (CH_CONSULTANT, 'Consultants'),
        (CH_ALUMNI, 'Alumni'),
        (CH_AMBASSADORS, 'Ambassadors'),
        (CH_TRAINER, 'Trainers'),
        (CH_INVESTOR, 'Investors')
    )

    WITH_CERTIFICATION = (
        CH_COACH, CH_AMBASSADORS, CH_TRAINER, CH_CONSULTANT
    )
