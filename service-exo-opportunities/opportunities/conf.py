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


class OpportunitiesConfig(AppConf):
    APP_NAME = 'opportunities'

    DELIVERY_MANAGER_GROUP = 'delivery-manager'

    # Opportunity status

    CH_DRAFT = 'X'
    CH_REQUESTED = 'R'
    CH_CLOSED = 'L'
    CH_REMOVED = 'M'

    CH_STATUS = (
        (CH_DRAFT, 'Draft'),
        (CH_REQUESTED, 'Requested'),
        (CH_REMOVED, 'Removed'),
        (CH_CLOSED, 'Closed'),
    )

    CH_STATUS_DEFAULT = CH_DRAFT

    # Permissions for Opportunity

    PERMS_EDIT_OPPORTUNITY = 'edit_opportunity'
    PERMS_REMOVE_OPPORTUNITY = 'remove_opportunity'
    PERMS_EDIT_ADMIN_OPPORTUNITY = 'edit_admin_opportunity'
    PERMS_ASSIGN_OPPORTUNITY = 'assign_opportunity'

    PERMS_ALL_PERMISSIONS = (
        (PERMS_EDIT_OPPORTUNITY, 'Edit Opportunity'),
        (PERMS_REMOVE_OPPORTUNITY, 'Remove Opportunity'),
        (PERMS_EDIT_ADMIN_OPPORTUNITY, 'Edit admin Opportunity'),
        (PERMS_ASSIGN_OPPORTUNITY, 'Assign Opportunity'),
    )
    FULL_PERMS_EDIT_ADMIN = '{}.{}'.format(
        APP_NAME,
        PERMS_EDIT_ADMIN_OPPORTUNITY)

    DESCRIPTION_CONSULTANT_ASSIGNED = 'Consultant: {}, assigned'

    CH_DEFAULT_ORDER_BY_STATUS = (
        (CH_DRAFT, 1),
        (CH_REQUESTED, 2),
        (CH_REMOVED, 4),
    )

    NAME_GROUP_ADMIN = 'new-opportunities-support'

    CH_APPLICANT_DRAFT = 'F'
    CH_APPLICANT_REQUESTED = 'B'
    CH_APPLICANT_REJECTED = 'J'
    CH_APPLICANT_REMOVED = 'V'
    CH_APPLICANT_SELECTED = 'G'
    CH_APPLICANT_COMPLETED = 'A'
    CH_APPLICANT_FEEDBACK_REQUESTER = 'C'
    CH_APPLICANT_FEEDBACK_APP = 'E'
    CH_APPLICANT_FEEDBACK_READY = 'H'

    CH_APPLICANT_STATUS = (
        (CH_APPLICANT_DRAFT, 'Draft'),
        (CH_APPLICANT_REQUESTED, 'Requested'),
        (CH_APPLICANT_REJECTED, 'Rejected'),
        (CH_APPLICANT_REMOVED, 'Removed'),
        (CH_APPLICANT_SELECTED, 'Selected'),
        (CH_APPLICANT_COMPLETED, 'Completed'),
        (CH_APPLICANT_FEEDBACK_REQUESTER, 'Feedback requester received'),
        (CH_APPLICANT_FEEDBACK_APP, 'Feedback applicant received'),
        (CH_APPLICANT_FEEDBACK_READY, 'Feedback received'),
    )

    CH_TARGET_OPEN = 'O'
    CH_TARGET_FIXED = 'F'

    CH_TARGET = (
        (CH_TARGET_OPEN, 'Opened'),
        (CH_TARGET_FIXED, 'Tagged'),
    )

    MAIL_VIEW_NEW_OPPORTUNITY = 'new_opportunity_created'
    MAIL_VIEW_NEW_OPPORTUNITY_WITHOUT_AGREEMENT = 'new_opportunity_created_not_signed_agreement'
    MAIL_VIEW_RESPOND_APPLICANT = 'opportunity_respond_applicant'
    MAIL_VIEW_APPLICANT_NOT_SELECTED = 'opportunity_applicant_not_selected'
    MAIL_VIEW_CLOSED_MANUALLY = 'opportunity_closed_applicant'
    MAIL_VIEW_CLOSED_BY_POSITIONS = 'opportunity_closed_requester'
    MAIL_VIEW_APPLICANT_SELECTED = 'opportunity_applicant_selected'
    MAIL_VIEW_OPPORTUNITY_REMOVED = 'opportunity_removed'
    MAIL_VIEW_OPPORTUNITY_EDITED = 'opportunity_edited'
    MAIL_VIEW_CLOSE_REMINDER = 'opportunity_reminder_close'
    MAIL_VIEW_DAILY_SUMMARY_SIGNED = 'opportunity_summary'
    MAIL_VIEW_DAILY_SUMMARY_NOT_SIGNED = 'opportunity_summary_not_signed_agreement'

    ACTION_CH_APPLY_OPEN = 'O'
    ACTION_CH_RE_OPEN = 'G'
    ACTION_CH_EDIT = 'E'
    ACTION_CH_SEND = 'S'
    ACTION_CH_REMOVE = 'R'
    ACTION_CH_ASSIGN = 'T'
    ACTION_CH_REJECT = 'D'
    ACTION_CH_ACCEPT = 'K'
    ACTION_CH_DECLINE = 'N'
    ACTION_CH_CLOSE = 'C'
    ACTION_CH_CREATE = 'A'
    ACTION_CH_SEE = 'B'
    ACTION_CH_SOW_EDIT = 'H'
    ACTION_CH_FEEDBACK = 'F'

    HISTORY_NO_USER_NAME = 'OpenExO'

    ADMIN_ACTIONS = [
        ACTION_CH_CLOSE,
        ACTION_CH_EDIT, ACTION_CH_REMOVE,
    ]

    PUBLIC_URL = '/ecosystem/opportunities/'

    APPLICANT_URL = '/ecosystem/opportunities/{}/'
    ADMIN_URL = '/ecosystem/opportunities/admin/{}/'
    FEEDBACK_ADMIN_URL = '/ecosystem/opportunities/admin/{}/feedback'
    CHAT_ADMIN_URL = '/ecosystem/opportunities/admin/{}/conversations'
    FEEDBACK_URL = '/ecosystem/opportunities/{}/feedback'
    CHAT_URL = '/ecosystem/opportunities/{}/chat'

    # Currencies

    CH_CURRENCY_EUR = 'E'
    CH_CURRENCY_DOLLAR = 'D'
    CH_CURRENCY_DEFAULT = CH_CURRENCY_DOLLAR

    CH_CURRENCY = (
        (CH_CURRENCY_EUR, 'EUR'),
        (CH_CURRENCY_DOLLAR, 'USD'),
    )

    CH_CURRENCY_EXOS = 'X'
    CH_VIRTUAL_CURRENCY_DEFAULT = CH_CURRENCY_EXOS
    CH_VIRTUAL_CURRENCY = (
        (CH_CURRENCY_EXOS, 'EXOS'),
    )

    # Location mode

    CH_MODE_ONSITE = 'S'
    CH_MODE_ONLINE = 'L'
    CH_MODE_DEFAULT = CH_MODE_ONSITE
    CH_MODE_CHOICES = (
        (CH_MODE_ONSITE, 'OnSite'),
        (CH_MODE_ONLINE, 'OnLine'),
    )

    # Question types

    QUESTION_CH_TYPE_BOOLEAN = 'B'
    QUESTION_CH_TYPE_DEFAULT = QUESTION_CH_TYPE_BOOLEAN
    QUESTION_CH_TYPE_CHOICES = (
        (QUESTION_CH_TYPE_BOOLEAN, 'Boolean'),
    )

    IS_NEW_TIMEDELTA_DAYS = 7

    ACT_ACTION_SEE = 'see'

    CHANNELS_HELLO = 'hello'
    CHANNELS_START = 'start'
    CHANNELS_CREATE = 'create'
    CHANNELS_NEW_CONVERSATION = 'new_conversation'

    CH_HUB_CONSULTANT = 'T'
    ACTION_NEW_OPPORTUNITY = 'new-opportunity'
    ACTION_NEW_APPLICANT = 'new-applicant'
    ACTION_REMOVED_OPPORTUNITY = 'removed-opportunity'
    ACTION_EDITED_OPPORTUNITY = 'edited-opportunity'

    CH_CLOSE_MANUALLY = 'M'
    CH_CLOSE_POSITIONS = 'P'
    CH_CLOSE_DEADLINE = 'D'

    DEADLINE_REMINDER = (
        (3, '3 days'),
        (1, '24 hours'),
    )

    ROL_CH_HEAD_COACH = 'M'
    ROL_CH_COACH = 'X'
    ROL_CH_SPEAKER = 'S'
    ROL_CH_EXO_FOUNDATIONS = 'EF'
    ROL_CH_DISRUPTOR = 'D'
    ROL_CH_CONSULTANT = 'EC'
    ROL_CH_EXO_TRAINER = 'TR'
    ROL_CH_OTHER = 'OT'

    CH_EXO_ROLES = (
        (ROL_CH_HEAD_COACH, 'head_coach'),
        (ROL_CH_COACH, 'coach'),
        (ROL_CH_SPEAKER, 'speaker'),
        (ROL_CH_EXO_FOUNDATIONS, 'exo_foundations'),
        (ROL_CH_DISRUPTOR, 'disruptor'),
        (ROL_CH_CONSULTANT, 'exo_consultant'),
        (ROL_CH_EXO_TRAINER, 'exo_trainer'),
        (ROL_CH_OTHER, 'other'),
    )

    JOB_DONE = 'D'
    JOB_NOT_COMPLETED = 'N'

    APPLICANT_JOB_STATUS = (
        (JOB_DONE, 'Done'),
        (JOB_NOT_COMPLETED, 'Not completed'),
    )

    DURATION_UNITY_MINUTE = 'T'
    DURATION_UNITY_HOUR = 'H'
    DURATION_UNITY_DAY = 'D'
    DURATION_UNITY_WEEK = 'W'
    DURATION_UNITY_MONTH = 'M'

    DURATION_UNITY_CHOICES = (
        (DURATION_UNITY_MINUTE, 'Minute'),
        (DURATION_UNITY_HOUR, 'Hour'),
        (DURATION_UNITY_DAY, 'Day'),
        (DURATION_UNITY_WEEK, 'Week'),
        (DURATION_UNITY_MONTH, 'Month'),
    )

    SEND_WHEN_CREATED = False

    CH_CONTEXT_EVENT = 'event'
    CH_CONTEXT_PROJECT = 'project'

    CH_CONTEXT = (
        (CH_CONTEXT_EVENT, 'Event'),
        (CH_CONTEXT_PROJECT, 'Project'),
    )

    CH_GROUP_TEAM = 'T'
    CH_GROUP_EXO_TEAM = 'E'

    CH_GROUP_ORIGIN = (
        (CH_GROUP_TEAM, 'Team'),
        (CH_GROUP_EXO_TEAM, 'ExO Projects Team'),
    )
