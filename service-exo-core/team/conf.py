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

    # ##
    # Permissions for Sprint Team
    # ##
    PERMS_FULL_VIEW_TEAM = 'team_full_view'
    PERMS_COACH_TEAM = 'coach_team'
    PERMS_CONSULTANT_TEAM = 'consultant_team'
    PERMS_TEAM_DELETE_EXOPROJECT = 'team_delete_exoproject'
    PERMS_START_MEETING = 'team_start_meeting'

    ALL_PERMISSIONS = (
        (PERMS_FULL_VIEW_TEAM, 'Team included'),
        (PERMS_COACH_TEAM, 'Team coach'),
        (PERMS_CONSULTANT_TEAM, 'Team consultant'),
        (PERMS_TEAM_DELETE_EXOPROJECT, 'Team: Delete ExO Project'),
        (PERMS_START_MEETING, 'Team: Start a meeting'),
    )

    FULL_VIEW = '{}.{}'.format(APP_NAME, PERMS_FULL_VIEW_TEAM)
    FULL_COACH = '{}.{}'.format(APP_NAME, PERMS_COACH_TEAM)

    ACTION_FEEDBACK_WEEKLY = 'feedback-team-step'
    ACTION_COMMENT_WEEKLY = 'comment-team-step'
