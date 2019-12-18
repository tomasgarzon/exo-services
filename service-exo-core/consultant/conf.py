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


class ConsultantConfig(AppConf):
    APP_NAME = 'consultant'

    # Consultant Status
    STATUS_CH_ACTIVE = 'A'
    STATUS_CH_DISABLED = 'D'
    STATUS_CH_PENDING_VALIDATION = 'P'
    STATUS_DEFAULT = STATUS_CH_PENDING_VALIDATION

    STATUS_CH_STATUS = (
        (STATUS_CH_ACTIVE, 'Active'),
        (STATUS_CH_DISABLED, 'Disabled'),
        (STATUS_CH_PENDING_VALIDATION, 'Pending validation'),
    )

    # Consultant Public Web Status
    WEB_CH_STATUS = (
        (STATUS_CH_ACTIVE, 'Active'),
        (STATUS_CH_DISABLED, 'Disabled'),
        (STATUS_CH_PENDING_VALIDATION, 'Pending'),
    )

    SPEAKERS_SITE = 'S'
    EXO_WORKS_SITE = 'W'

    PUBLIC_SITES = (
        (SPEAKERS_SITE, 'Speakers Site'),
        (EXO_WORKS_SITE, 'ExO Works Site'),
    )

    # Validation types
    VALIDATION_AGREEMENT = 'G'
    VALIDATION_SKILL_ASSESSMENT = 'S'
    VALIDATION_APPLICATION = 'A'
    VALIDATION_TEST = 'T'
    VALIDATION_USER = 'U'
    VALIDATION_BASIC_PROFILE = 'F'

    VALIDATION_CH_TYPE = (
        (VALIDATION_AGREEMENT, 'Agreement'),
        (VALIDATION_SKILL_ASSESSMENT, 'Skill Assessment'),
        (VALIDATION_APPLICATION, 'Application'),
        (VALIDATION_TEST, 'Test'),
        (VALIDATION_USER, 'User'),
        (VALIDATION_BASIC_PROFILE, 'On boarding'),
    )

    VALIDATION_FRONTEND_CH_TYPE = {
        VALIDATION_AGREEMENT: 'Agreement',
        VALIDATION_SKILL_ASSESSMENT: 'Skill Assessment',
        VALIDATION_APPLICATION: 'Application',
        VALIDATION_TEST: 'Test',
        VALIDATION_USER: 'Invitation',
        VALIDATION_BASIC_PROFILE: 'On boarding',
    }

    # Validation status
    VALIDATION_CH_WAITING = 'W'
    VALIDATION_CH_SENT = 'S'
    VALIDATION_CH_SENT_SKIPPED = 'K'
    VALIDATION_CH_PENDING_REVIEW = 'P'
    VALIDATION_CH_ACCEPTED = 'A'
    VALIDATION_CH_DENIED = 'D'

    VALIDATION_CH_STATUS = (
        (VALIDATION_CH_WAITING, 'Waiting to send'),
        (VALIDATION_CH_SENT, 'Sent'),
        (VALIDATION_CH_SENT_SKIPPED, 'Notification skipped'),
        (VALIDATION_CH_PENDING_REVIEW, 'Pending'),
        (VALIDATION_CH_ACCEPTED, 'Accepted'),
        (VALIDATION_CH_DENIED, 'Denied'),
    )

    VALIDATION_STATUS_PUBLIC_LOG = [
        VALIDATION_CH_WAITING,
        VALIDATION_CH_SENT,
        VALIDATION_CH_PENDING_REVIEW,
        VALIDATION_CH_ACCEPTED,
        VALIDATION_CH_DENIED,
    ]

    # SOCIAL NETWORK TYPES
    SOCIAL_SKYPE = 'S'
    SOCIAL_LINKEDIN = 'L'
    SOCIAL_TWITTER = 'T'
    SOCIAL_MEDIUM = 'M'
    SOCIAL_FACEBOOK = 'F'
    PERSONAL_WEBSITE = 'P'
    PERSONAL_LINK = 'N'

    SOCIAL_TYPES = (
        SOCIAL_SKYPE,
        SOCIAL_LINKEDIN,
        SOCIAL_TWITTER,
        SOCIAL_MEDIUM,
        PERSONAL_WEBSITE,
        SOCIAL_FACEBOOK,
    )

    CH_SOCIAL_NETWORK = (
        (SOCIAL_SKYPE, 'Skype'),
        (SOCIAL_LINKEDIN, 'Linkedin'),
        (SOCIAL_TWITTER, 'Twitter'),
        (SOCIAL_MEDIUM, 'Medium'),
        (PERSONAL_WEBSITE, 'Website'),
        (SOCIAL_FACEBOOK, 'Facebook'),
    )
    # PERMISSIONS
    PERMS_CONSULTANT_LIST_AND_EXPORT = 'consultant_list'
    PERMS_CONSULTANT_EDIT_PROFILE = 'consultant_edit_profile'
    PERMS_CONSULTANT_VIEW_FULL_PROFILE = 'consultant_view_full_profile'
    PERMS_EDIT_REGISTRATION_PROCESS = 'registration_process_edit'

    ALL_PERMISSIONS = (
        (PERMS_CONSULTANT_LIST_AND_EXPORT, 'List&Export consultants'),
        (PERMS_CONSULTANT_EDIT_PROFILE, 'Edit consultants'),
        (PERMS_CONSULTANT_VIEW_FULL_PROFILE, 'View Full Profile'),
        (PERMS_EDIT_REGISTRATION_PROCESS, 'Edit Registration Process'),
    )

    FULL_PERMS_ADD_CONSULTANT = '{}.{}'.format(
        APP_NAME,
        'add_consultant',
    )

    FULL_PERMS_CONSULTANT_LIST_AND_EXPORT = '{}.{}'.format(
        APP_NAME,
        PERMS_CONSULTANT_LIST_AND_EXPORT,
    )

    SKILL_AVAILABILITY = (
        ('F', 'Fulltime'),
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly'),
    )

    SKILL_MTP_MASTERY_CHOICES = (
        (0, 'I haven’t read about it'),
        (1, 'I have read about it and understand it'),
        (2, 'I have studied it in some detail'),
        (3, 'I have implemented this once or twice'),
        (4, 'I have implemented this several times'),
        (5, 'I’m considered a thought leader in this domain, and I’ve published articles/papers about it'),
    )

    DEFAULT_LANGUAGES = ['English']

    WAITING_LIST_GROUP_NAME = 'waiting_list'
