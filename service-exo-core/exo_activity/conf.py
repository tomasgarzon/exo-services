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


class ExOActivityConfig(AppConf):

    APP_NAME = 'exo_activity'

    CH_ACTIVITY_ADVISING = 'advising'
    CH_ACTIVITY_COACHING = 'coaching'
    CH_ACTIVITY_CONSULTING = 'consulting'
    CH_ACTIVITY_SPEAKING = 'speaking'
    CH_ACTIVITY_BUSINESS_DEVELOPMENT = 'business_development'
    CH_ACTIVITY_CONTENT_GENERATION = 'content_generation'
    CH_ACTIVITY_INVESTOR = 'investor'
    CH_ACTIVITY_ENTREPRENEURSHIP = 'entrepreneurship'
    CH_ACTIVITY_TRAINING = 'training'
    CH_ACTIVITY_COMPANY_DEVELOPMENT = 'company_development'

    DEFAULT_CONSULTANT_EXO_ACTIVITIES = [CH_ACTIVITY_ADVISING]

    CH_EXO_CODE = (
        (CH_ACTIVITY_ADVISING, 'advising'),
        (CH_ACTIVITY_COACHING, 'coaching'),
        (CH_ACTIVITY_CONSULTING, 'consulting'),
        (CH_ACTIVITY_SPEAKING, 'speaking'),
        (CH_ACTIVITY_BUSINESS_DEVELOPMENT, 'business_development'),
        (CH_ACTIVITY_CONTENT_GENERATION, 'content_generation'),
        (CH_ACTIVITY_INVESTOR, 'investor'),
        (CH_ACTIVITY_ENTREPRENEURSHIP, 'entrepreneurship'),
        (CH_ACTIVITY_TRAINING, 'training'),
        (CH_ACTIVITY_COMPANY_DEVELOPMENT, 'company_development'),
    )

    EXOACTIVITY_PERMISSIONS = (
        (CH_ACTIVITY_ADVISING, 'Advising'),
        (CH_ACTIVITY_COACHING, 'Coaching'),
        (CH_ACTIVITY_CONSULTING, 'Consulting'),
        (CH_ACTIVITY_SPEAKING, 'Speaking'),
        (CH_ACTIVITY_BUSINESS_DEVELOPMENT, 'Business development'),
        (CH_ACTIVITY_CONTENT_GENERATION, 'Content generation'),
        (CH_ACTIVITY_INVESTOR, 'Investor'),
        (CH_ACTIVITY_ENTREPRENEURSHIP, 'Entrepreneurship'),
        (CH_ACTIVITY_TRAINING, 'Training'),
        (CH_ACTIVITY_COMPANY_DEVELOPMENT, 'Company development'),
    )

    PERM_CH_ACTIVITY_ADVISING = '{}.{}'.format(APP_NAME, CH_ACTIVITY_ADVISING)
    PERM_CH_ACTIVITY_CONSULTING = '{}.{}'.format(APP_NAME, CH_ACTIVITY_CONSULTING)

    CH_HUB_NAME = (
        (CH_ACTIVITY_ADVISING, ''),
        (CH_ACTIVITY_COACHING, ''),
        (CH_ACTIVITY_CONSULTING, 'T'),
        (CH_ACTIVITY_SPEAKING, ''),
        (CH_ACTIVITY_BUSINESS_DEVELOPMENT, ''),
        (CH_ACTIVITY_CONTENT_GENERATION, ''),
        (CH_ACTIVITY_INVESTOR, 'I'),
        (CH_ACTIVITY_ENTREPRENEURSHIP, ''),
        (CH_ACTIVITY_TRAINING, ''),
        (CH_ACTIVITY_COMPANY_DEVELOPMENT, ''),
    )
