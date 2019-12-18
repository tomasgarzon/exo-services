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
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class SurveyConfig(AppConf):
    APP_NAME = 'survey'

    CH_MTP = 'M'
    CH_STAFF_ON_DEMAND = 'S'
    CH_COMMUNITY_CROUD = 'C'
    CH_ALGORITHMS_DATA = 'A'
    CH_LEVERAGED_ASSETS = 'L'
    CH_ENGAGEMENT = 'E'
    CH_INTERFACES = 'I'
    CH_DASHBOARDS = 'D'
    CH_EXPERIMENTATION = 'X'
    CH_AUTONOMY = 'F'
    CH_SOCIAL = 'O'
    CH_BUSINESS_MODEL = 'B'

    CH_SECTION = (
        (CH_MTP, _('Massive Transformative Purpose')),
        (CH_STAFF_ON_DEMAND, _('Staff on-demand')),
        (CH_COMMUNITY_CROUD, _('Community & Crowd')),
        (CH_ALGORITHMS_DATA, _('Algorithms')),
        (CH_LEVERAGED_ASSETS, _('Leveraged Assets')),
        (CH_ENGAGEMENT, _('Engagement')),
        (CH_INTERFACES, _('Interfaces')),
        (CH_DASHBOARDS, _('Dashboards')),
        (CH_EXPERIMENTATION, _('Experimentation')),
        (CH_AUTONOMY, _('Autonomy')),
        (CH_SOCIAL, _('Social')),
        (CH_BUSINESS_MODEL, _('Business Type Model'))
    )

    PERMS_VIEW = 'view_survey'
    RESULT_FOR_USER = 'survey_result_user'

    CH_ENGLISH = 'en'
    CH_SPANISH = 'es'

    CH_LANGUAGES = (
        (CH_ENGLISH, 'English'),
        (CH_SPANISH, 'Spanish')
    )
