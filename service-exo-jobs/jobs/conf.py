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


class JobConfig(AppConf):
    APP_NAME = 'job'

    CH_STATUS_UNSTARTED = 'UP'
    CH_STATUS_LIVE = 'LI'
    CH_STATUS_RUNNING = 'IN'
    CH_STATUS_FINISHED = 'CO'
    CH_STATUS_UNKNOWN = 'UN'

    STATUS_CHOICES = (
        (CH_STATUS_UNSTARTED, 'Upcoming'),
        (CH_STATUS_LIVE, 'Live'),
        (CH_STATUS_RUNNING, 'In Progress'),
        (CH_STATUS_FINISHED, 'Completed'),
        (CH_STATUS_UNKNOWN, 'Unknown'),
    )

    CH_CLASS_CORE_PROJECT = 'CP'
    CH_CLASS_EXO_PROJECT = 'CX'
    CH_CLASS_OPP = 'CO'
    CH_CLASS_EVENT = 'CE'

    CLASS_CHOICES = (
        (CH_CLASS_CORE_PROJECT, 'CoreProject'),
        (CH_CLASS_EXO_PROJECT, 'ExOProject'),
        (CH_CLASS_OPP, 'Opportunity'),
        (CH_CLASS_EVENT, 'Event'),
    )
