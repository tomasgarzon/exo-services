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


class TeamConfig(AppConf):
    APP_NAME = 'team'

    ACTION_FEEDBACK_WEEKLY = 'feedback-team-step'
    ACTION_COMMENT_WEEKLY = 'comment-team-step'

    # Stream types
    STREAM_CH_EDGE = 'E'
    STREAM_CH_CORE = 'C'
    STREAM_CH_UNIQUE = 'U'
    STREAM_CH_TYPE_DEFAULT = STREAM_CH_EDGE

    STREAM_CH_TYPE = (
        (STREAM_CH_EDGE, 'Edge Stream'),
        (STREAM_CH_CORE, 'Core Stream'),
        (STREAM_CH_UNIQUE, 'Unique'),
    )

    CH_ROLE_LEVEL_ADMIN = 'admin'
    CH_ROLE_LEVEL_BASIC = 'basic'
    CH_ROLE_LEVEL_READONLY = 'readonly'
    CH_ROLE_LEVEL_NOTIFICATIONS = 'notification'
    CH_ROLE_LEVEL_DEFAULT = CH_ROLE_LEVEL_BASIC

    ROLE_LEVEL = (
        (CH_ROLE_LEVEL_ADMIN, 'Admin'),
        (CH_ROLE_LEVEL_BASIC, 'Basic'),
        (CH_ROLE_LEVEL_READONLY, 'Readonly'),
        (CH_ROLE_LEVEL_NOTIFICATIONS, 'Notification'),
    )

    ALL_PERMISSIONS = ROLE_LEVEL

    CH_ACTION_EDIT = 'E'
    CH_ACTION_DELETE = 'D'
    CH_ACTION_PARTICIPANTS = 'P'

    CH_ACTION_USER_TEAM_EDIT_PARTICIPANT = 'E'
    CH_ACTION_USER_TEAM_EDIT_ROLES = 'R'
    CH_ACTION_USER_TEAM_EDIT_TEAMS = 'T'
    CH_ACTION_USER_TEAM_UNSELECT = 'S'
    CH_ACTION_USER_TEAM_MOVE = 'V'

    IMAGES = {
        STREAM_CH_CORE: [
            'https://cdn.filestackcontent.com/kpRzP37Tw6Hdp2iqinjw',
            'https://cdn.filestackcontent.com/4J7o0xYFSXK6bODeKgli',
            'https://cdn.filestackcontent.com/qlFWPUyjQxC6fNF4rZRU',
        ],
        STREAM_CH_EDGE: [
            'https://cdn.filestackcontent.com/zmVW1DkCRzuWwYMWSO9Y',
            'https://cdn.filestackcontent.com/vTk5DILsRimLEH8G1foW',
            'https://cdn.filestackcontent.com/yiz0S1aSqmrzpvz9Vky9',
        ],
        STREAM_CH_UNIQUE: []
    }
