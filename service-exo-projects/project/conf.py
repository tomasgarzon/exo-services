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


class ProjectConfig(AppConf):
    APP_NAME = 'project'

    # Project Status
    CH_STATUS_WAITING = 'W'
    CH_STATUS_DRAFT = 'D'
    CH_STATUS_STARTED = 'S'
    CH_STATUS_FINISHED = 'F'
    CH_STATUS_REMOVED = 'R'

    CH_STATUS = (
        (CH_STATUS_STARTED, 'Active'),
        (CH_STATUS_WAITING, 'Waiting'),
        (CH_STATUS_DRAFT, 'Draft'),
        (CH_STATUS_FINISHED, 'Finished'),
        (CH_STATUS_REMOVED, 'Removed'),
    )

    CH_PROJECT_INTERNAL_STATUS = (
        (CH_STATUS_DRAFT, 'draft'),
        (CH_STATUS_WAITING, 'waiting'),
        (CH_STATUS_STARTED, 'started'),
        (CH_STATUS_FINISHED, 'finished'),
        (CH_STATUS_REMOVED, 'removed'),
    )

    CH_STATUS_STEP_FUTURE = 'F'
    CH_STATUS_STEP_CURRENT = 'C'
    CH_STATUS_STEP_PAST = 'P'

    CH_STATUS_STEP = (
        (CH_STATUS_STEP_FUTURE, 'Future'),
        (CH_STATUS_STEP_CURRENT, 'Current'),
        (CH_STATUS_STEP_PAST, 'Past'),
    )

    FOLDER_PREFIX = 'project'

    CH_ZONE_ADMIN = 'admin'

    CH_ACCOMPLISH_1 = '1'
    CH_ACCOMPLISH_2 = '2'
    CH_ACCOMPLISH_3 = '3'

    CH_ACCOMPLISH = (
        (CH_ACCOMPLISH_1, 'To reinvent the industry and transform our organization'),
        (CH_ACCOMPLISH_2, 'To transform our organization so that it’s able to adapt to external industry disruption'),
        (CH_ACCOMPLISH_3, 'To launch an ExO or multiple ExOs in order to transform the industry'),
    )

    CH_TRANSFORM_1 = '1'
    CH_TRANSFORM_2 = '2'
    CH_TRANSFORM_3 = '3'

    CH_TRANSFORM = (
        (CH_TRANSFORM_1, 'The organisation as a whole, including all markets and industries in which it is positioned'),
        (CH_TRANSFORM_2, 'A specific business unit focused on a particular industry'),
    )

    CH_PLAYGROUND_1 = '1'
    CH_PLAYGROUND_2 = '2'
    CH_PLAYGROUND_3 = '3'

    CH_PLAYGROUND = (
        (CH_PLAYGROUND_1, 'Any industry'),
        (CH_PLAYGROUND_2, 'Adjacent industries'),
        (CH_PLAYGROUND_3, 'Our current industry, with a goal of creating an ExO'),
    )

    CH_PROJECT_TEMPLATE_BLANK = 'blank'
    CH_PROJECT_TEMPLATE_AUTOMATED = 'automated'
    CH_PROJECT_TEMPLATE_FASTRACK = 'fastrack'
    CH_PROJECT_TEMPLATE_DEFAULT = CH_PROJECT_TEMPLATE_AUTOMATED

    CH_PROJECT_TEMPLATE = (
        (CH_PROJECT_TEMPLATE_AUTOMATED, 'Automated'),
        (CH_PROJECT_TEMPLATE_FASTRACK, 'Fastrack'),
        (CH_PROJECT_TEMPLATE_BLANK, 'Blank'),
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

    CH_CATEGORY_TRAINING = 'T'
    CH_CATEGORY_CERTIFICATION = 'C'
    CH_CATEGORY_CERTIFICATION_CONSULTANT = 'CC'
    CH_CATEGORY_CERTIFICATION_SPRINT_COACH = 'CX'
    CH_CATEGORY_DEMO = 'D'
    CH_CATEGORY_TRANSFORMATION = 'M'
    CH_CATEGORY_DEFAULT = CH_CATEGORY_TRANSFORMATION

    CH_CATEGORY = (
        (CH_CATEGORY_TRAINING, 'Training'),
        (CH_CATEGORY_CERTIFICATION, 'Certification'),
        (CH_CATEGORY_CERTIFICATION_CONSULTANT, 'Certification ExO Consultant'),
        (CH_CATEGORY_CERTIFICATION_SPRINT_COACH, 'Certification ExO Sprint Coach'),
        (CH_CATEGORY_DEMO, 'Demo'),
        (CH_CATEGORY_TRANSFORMATION, 'Transformation'),
    )

    TEMPLATE_NAME_DEFAULT = 'ExO Sprint'

    ALL_PERMISSIONS = ROLE_LEVEL

    STEP_FEEDBACK_FROM_COACH = 1
    STEP_FEEDBACK_FROM_TEAM_MEMBERS = 2

    CH_ACTION_EDIT = 'E'
    CH_ACTION_LAUNCH = 'L'
    CH_ACTION_DELETE = 'D'

    CH_ACTION_USER_EDIT_PARTICIPANT = 'E'
    CH_ACTION_USER_EDIT_ROLES = 'R'
    CH_ACTION_USER_EDIT_TEAMS = 'T'
    CH_ACTION_USER_UNSELECT = 'S'

    CH_ZONE_BACKOFFICE = 'B'
    CH_ZONE_PROJECT = 'P'
    CH_ZONE_PROFILE = 'F'

    EMAIL_MEMBER_LAUNCH = 'projects_member_launch'
    EMAIL_LOCATION_CHANGED = 'projects_location_changed'
    EMAIL_MEMBER_ADDED_TEAM = 'projects_member_added_to_team'
    EMAIL_MEMBER_REMOVED = 'projects_member_removed'
    EMAIL_ROLE_CHANGED = 'projects_member_role_changed'
    EMAIL_START_CHANGED = 'projects_start_changed'

    CH_GROUP_GENERAL = 'General'
    CH_GROUP_COLLABORATORS = 'Collaborators'
    CH_GROUP_TEAMS = 'Teams'
    CH_GROUP_TEAM = 'Team'

    CH_GROUP_CHOICES = (
        (CH_GROUP_GENERAL, 'General'),
        (CH_GROUP_COLLABORATORS, 'Collaborators'),
        (CH_GROUP_TEAMS, 'Teams'),
        (CH_GROUP_TEAM, 'Team'),
    )

    TOPIC_NAME = 'project'
    URL_PROFILE = '/ecosystem/workspace/projects/{}/summary'
    URL_ZONE = '/platform/service/exo/{}/team/{}/step/{}'
    CHAT_URL = '/platform/service/exo/{}/team/{}/team-communication'
    ADVISOR_URL = '/platform/service/exo/{}/team/{}/requests'
