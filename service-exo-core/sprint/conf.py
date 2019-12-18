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


class SprintConfig(AppConf):

    # ##
    # Stream types
    # ##
    STREAM_CH_STARTUP = 'S'
    STREAM_CH_STRATEGY = 'T'
    STREAM_CH_TECHNOLOGY = 'X'

    STREAM_CH_TYPE_DEFAULT = STREAM_CH_STARTUP

    STREAM_CH_TYPE = (
        (STREAM_CH_STARTUP, 'Startup Ecosystems'),
        (STREAM_CH_STRATEGY, 'ExO Lite'),
    )

    # ##
    # Permissions for Sprint Team
    # ##
    PERMS_FULL_VIEW_TEAM = 'team_full_view'
    PERMS_COACH_TEAM = 'coach_team'
    PERMS_START_MEETING = 'team_start_meeting'

    TEAM_ALL_PERMISSIONS = (
        (PERMS_FULL_VIEW_TEAM, 'Team included'),
        (PERMS_COACH_TEAM, 'Team coach'),
        (PERMS_START_MEETING, 'Team: Start a meeting'),
    )

    TEAM_FULL_VIEW = 'sprint.' + PERMS_FULL_VIEW_TEAM

    WEEK_DESCRIPTION = [
        (
            'To define the current organization and complete the ExQ Assessment.',
            'To identify and research technologies and startups that may disrupt your industry.',
        ),
        (
            'To define the goal and the high-level approach of the ExO Lite implementation for the organization.',
            'To define potential projects (at least 4) based on the found startups and technologies.',
        ),
        (
            'To define the ExO Lite foundations (MTP, ExO Canvas and ExO Attributes) to implement the ExO model.',
            'To evaluate the business model of the projects and narrow down the list (keep at least 3 projects).',
        ),
        (
            'To draft the public presentation for the disruption workshop on the ExO Lite project.',
            'To draft the public presentations for the disruption workshop on the ExO on the Edge projects.',
        ),
        (
            'To do a general review and a public presentation for the disruption workshop.',
            'To do a general review and a public presentation for the disruption workshop.',
        ),
        (
            'To adapt the ExO Lite approach & foundations based on feedback from the disruption workshop.',
            'To narrow down to 2 and adapt the projects; and create a new one based after the disruption workshop.',
        ),
        (
            'To further define the ExO foundations (WHY, HOW and WHAT).',
            'To further define the ExO foundations for the remaining projects.',
        ),
        (
            'To gather data and run experiments to evaluate the final set of ExO Attributes to implement.',
            'To gather data and run experiments to evaluate the final set of ExO and its business models.',
        ),
        (
            'To make final recommendations and next steps on 4 ExO Attributes to implement.',
            'To make final recommendations and a first draft of the final presentation.',
        ),
        (
            'To do presentations for the final ExO Lite Project.',
            'To do presentations for the final ExO projects.',
        ),
    ]

    DURATION_WEEK = 10
