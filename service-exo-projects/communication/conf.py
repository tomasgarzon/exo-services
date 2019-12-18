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


class CommunicationConfig(AppConf):
    APP_NAME = 'communication'
    CH_GENERAL = 'G'
    CH_COLLABORATORS = 'C'
    CH_TEAM = 'T'

    CH_TYPE_CHOICES = (
        (CH_GENERAL, 'General'),
        (CH_COLLABORATORS, 'Collaborators'),
        (CH_TEAM, 'Team'),
    )
