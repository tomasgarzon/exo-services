# -*- coding: utf-8 -*-
"""
License boilerplate should be used here.
"""

from __future__ import absolute_import, unicode_literals

import logging

from appconf import AppConf

from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class ProjectConfig(AppConf):

    APP_NAME = 'project'

    # ##
    # Available services
    # ##

    CH_TYPE_SPRINT = 'sprint'
    CH_TYPE_SPRINT_AUTOMATED = 'sprintautomated'
    CH_TYPE_GENERIC_PROJECT = 'genericproject'
    CH_TYPE_WORKSHOP = 'workshop'
    CH_TYPE_FASTRACKSPRINT = 'fastracksprint'
    CH_TYPE_FASTRACK = 'fastrack'

    AVAILABLE_SERVICES = [
        CH_TYPE_SPRINT,
        CH_TYPE_SPRINT_AUTOMATED,
        CH_TYPE_GENERIC_PROJECT,
        CH_TYPE_FASTRACKSPRINT,
        CH_TYPE_FASTRACK,
    ]

    CH_TYPE_PROJECT = (
        (CH_TYPE_SPRINT, CH_TYPE_SPRINT),
        (CH_TYPE_SPRINT_AUTOMATED, CH_TYPE_SPRINT_AUTOMATED),
        (CH_TYPE_GENERIC_PROJECT, CH_TYPE_GENERIC_PROJECT),
        (CH_TYPE_WORKSHOP, CH_TYPE_WORKSHOP),
        (CH_TYPE_FASTRACKSPRINT, CH_TYPE_FASTRACKSPRINT),
    )

    LAPSE_WEEK = 'W'
    LAPSE_DAY = 'D'
    LAPSE_PERIOD = 'P'
    LAPSE_NO_APPLY = 'N'

    CH_LAPSE = (
        (LAPSE_WEEK, 'Week'),
        (LAPSE_DAY, 'Day'),
        (LAPSE_PERIOD, 'Period'),
        (LAPSE_NO_APPLY, 'No step'),
    )

    # ##
    # Project Permissions
    # ##

    PERMS_ADD_PROJECT = 'add_project'
    PERMS_DELETE_PROJECT = 'delete_project'
    PERMS_EDIT_PROJECT = 'edit_project'
    PERMS_VIEW_PROJECT = 'full_view'
    PERMS_ONLY_VIEW_PROJECT = 'only_view'
    PERMS_PROJECT_MANAGER = 'project_manager'
    PERMS_PROJECT_CONSULTANT = 'project_consultant'
    PERMS_PROJECT_SURVEYS = 'project_assessment'
    PERMS_PROJECT_MANAGE_CONSULTANT = 'project_manage_consultant'
    PERMS_PROJECT_SETTINGS = 'project_settings'
    PERMS_DELIVERY_MANAGER = 'manage_ticket'
    PERMS_CRUD_TEAM = 'crud_team'

    ALL_PERMISSIONS = (
        (PERMS_EDIT_PROJECT, 'Edit Project'),
        (PERMS_VIEW_PROJECT, 'View Project'),
        (PERMS_ONLY_VIEW_PROJECT, 'Only view project'),
        (PERMS_CRUD_TEAM, 'Add/Edit/Delete Team'),
        (PERMS_PROJECT_MANAGER, 'Project Manager'),
        (PERMS_PROJECT_MANAGE_CONSULTANT, 'Manage ExO Consultants'),
        (PERMS_PROJECT_CONSULTANT, 'Project Consultant'),
        (PERMS_PROJECT_SURVEYS, 'Project ExO Assessment'),
        (PERMS_PROJECT_SETTINGS, 'Project Settings'),
        (PERMS_DELIVERY_MANAGER, 'Project Delivery management'),
    )

    FULL_VIEW = APP_NAME + '.' + PERMS_VIEW_PROJECT
    ADD_PROJECT = APP_NAME + '.' + PERMS_ADD_PROJECT

    # ##
    # Project Status
    # ##

    CH_PROJECT_STATUS_WAITING = 'W'
    CH_PROJECT_STATUS_DRAFT = 'D'
    CH_PROJECT_STATUS_STARTED = 'S'
    CH_PROJECT_STATUS_FINISHED = 'F'

    CH_PROJECT_STATUS = (
        (CH_PROJECT_STATUS_WAITING, 'Not Started'),
        (CH_PROJECT_STATUS_DRAFT, 'Draft'),
        (CH_PROJECT_STATUS_STARTED, 'In progress'),
        (CH_PROJECT_STATUS_FINISHED, 'Finished'),
    )

    CH_PROJECT_INTERNAL_STATUS = (
        (CH_PROJECT_STATUS_WAITING, 'waiting'),
        (CH_PROJECT_STATUS_DRAFT, 'draft'),
        (CH_PROJECT_STATUS_STARTED, 'started'),
        (CH_PROJECT_STATUS_FINISHED, 'finished'),
    )

    FOLDER_PREFIX = 'project'

    # ##
    # Steps for Services
    # ##

    STEP_STATUS_WAITING = 'w'
    STEP_STATUS_STARTED = 's'
    STEP_STATUS_DONE = 'd'
    STEP_STATUS_DEFAULT = STEP_STATUS_WAITING

    CH_STEP_STATUS = (
        (STEP_STATUS_WAITING, 'Waiting'),
        (STEP_STATUS_STARTED, 'Started'),
        (STEP_STATUS_DONE, 'Done'),
    )

    CH_ZONE_ADMIN = 'admin'

    # ##
    # Stream types
    # ##
    STREAM_CH_STARTUP = 'S'
    STREAM_CH_STRATEGY = 'T'
    STREAM_CH_TECHNOLOGY = 'X'

    STREAM_CH_TYPE_DEFAULT = STREAM_CH_STARTUP

    STREAM_CH_TYPE = (
        (STREAM_CH_STARTUP, 'Edge Stream'),
        (STREAM_CH_STRATEGY, 'Core Stream'),
    )

    CH_VERSION_1 = '1'
    CH_VERSION_2 = '2'
    CH_VERSION_DEFAULT = CH_VERSION_2

    CH_VERSION = (
        (CH_VERSION_1, 'Version 1'),
        (CH_VERSION_2, 'Version 2'),
    )

    CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK = 'S'
    CH_TEMPLATE_ASSIGNMENTS_LEVEL_1_EN = 'B'
    CH_TEMPLATE_ASSIGNMENTS_LEVEL_1_ES = 'C'
    CH_TEMPLATE_ASSIGNMENTS_DEFAULT = CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK

    CH_TEMPLATE_ASSIGNMENTS = (
        (CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK, 'Sprint Book'),
        (CH_TEMPLATE_ASSIGNMENTS_LEVEL_1_EN, 'Certification Level 1'),
        (CH_TEMPLATE_ASSIGNMENTS_LEVEL_1_ES, 'Certificacion Nivel 1'),
    )

    MEDIA_LIBRARY_API_RESOURCES_LIST_DETAIL_ROUTE_ADD_TO_PROJECTS = 'add-to-projects'
    MEDIA_LIBRARY_API_RESOURCES_LIST_DETAIL_ROUTE_REMOVE_FROM_PROJECTS = 'remove-from-projects'

    STEP_FEEDBACK_FROM_COACH = 1
    STEP_FEEDBACK_FROM_TEAM_MEMBERS = 2

    TYPE_TO_TEMPLATE = {
        'EXO AUTOMATED SPRINT': 'ExO Sprint',
        'EXO CERTIFICATION WORKSHOP': 'ExO Workshop',
        'EXO GENERIC PROJECT': 'ExO Sprint',
        'EXO SPRINT': 'ExO Sprint',
        'FASTRACK': 'Fastrack',
        'SPRINTS AUTOMATED': 'ExO Sprint'
    }

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

    TOPIC_NAME = 'project'
