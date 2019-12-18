# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""
# python 3 imports
from __future__ import absolute_import, unicode_literals

# django imports
from django.conf import settings  # noqa

# 3rd. party imports
from appconf import AppConf


class AccountConfigConf(AppConf):
    GROUPS = {
        '*': {}
    }

    BOOLEAN = bool.__name__
    INTEGER = int.__name__
    ALLOWED_TYPES = (
        (BOOLEAN, 'boolean'),
        (INTEGER, 'integer'),
    )

    ASK_TO_ECOSYSTEM = 'ask_to_ecosystem'
    TEAM_COMMUNICATION = 'team_communication'
    SWARM_SESSION = 'swarm_sessions'
    CIRCLES = 'cicles'
    OPPORTUNITIES = 'opportunities'
    CHAT = 'chat'

    CONFIG_GROUPS = (
        (ASK_TO_ECOSYSTEM, 'Ask to Ecosystem'),
        (TEAM_COMMUNICATION, 'Team Communication'),
        (SWARM_SESSION, 'Swarm Sessions'),
        (CIRCLES, 'Circles'),
        (OPPORTUNITIES, 'Opportunities'),
        (CHAT, 'chat'),
    )

    class Meta:
        prefix = 'account_conf'
