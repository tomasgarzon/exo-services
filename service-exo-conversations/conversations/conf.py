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
from django.conf import settings  # NOQA

logger = logging.getLogger(__name__)


class ConversationsConfig(AppConf):
    APP_NAME = 'conversations'

    CH_OPPORTUNITIES = 'O'
    CH_PROJECT = 'P'
    CH_USER = 'U'
    CH_EXO_PROJECT = 'S'

    CH_OPTIONS = (
        (CH_OPPORTUNITIES, 'Opportunities'),
        (CH_PROJECT, 'Project'),
        (CH_EXO_PROJECT, 'ExO Project'),
        (CH_USER, 'User 1 to 1'),
    )

    ACTION_SEE = 'see'

    ACTION_NEW_CONVERSATION = 'new-conversations'
    ACTION_NEW_MESSAGE = 'new-message'
    ACTION_SEE_MESSAGE = 'see-message'
