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

    CH_CATEGORY_TICKET = 'TI'
    CH_CATEGORY_PROJECT = 'PR'
    CH_CATEGORY_EXO_PROJECT = 'EP'
    CH_CATEGORY_FASTRACK = 'FA'
    CH_CATEGORY_QASESSION = 'QA'
    CH_CATEGORY_OPPORTUNITY = 'OP'

    CATEGORY_CHOICES = (
        (CH_CATEGORY_TICKET, 'Ticket'),
        (CH_CATEGORY_PROJECT, 'Project'),
        (CH_CATEGORY_EXO_PROJECT, 'ExOProject'),
        (CH_CATEGORY_FASTRACK, 'Fastrack'),
        (CH_CATEGORY_QASESSION, 'QASession'),
        (CH_CATEGORY_OPPORTUNITY, 'Opportunity'),
    )

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
