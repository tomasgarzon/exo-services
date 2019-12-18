# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf import settings  # noqa
from django.utils.translation import ugettext_lazy as _

import logging

from appconf import AppConf


logger = logging.getLogger(__name__)


class ExOAccountsConfig(AppConf):
    app_name = 'exo_accounts'

    # ##
    # Languages configuration
    # ##

    LANGUAGE_EN = 'en'
    LANGUAGE_ES = 'es'
    LANGUAGE_PT = 'pt'
    LANGUAGE_JA = 'ja'
    LANGUAGE_ZH = 'zh-hans'

    LANGUAGE_DEFAULT = LANGUAGE_EN

    LANGUAGES = (
        (LANGUAGE_EN, _('English')),
        (LANGUAGE_ES, _('Spanish')),
        (LANGUAGE_PT, _('Portuguese')),
        (LANGUAGE_JA, _('Japanese')),
        (LANGUAGE_ZH, _('Simplified Chinese'))
    )

    # ##
    # SOCIAL NETWORK TYPES
    # ##

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
        SOCIAL_FACEBOOK
    )

    CH_SOCIAL_NETWORK = (
        (SOCIAL_SKYPE, 'Skype'),
        (SOCIAL_LINKEDIN, 'Linkedin'),
        (SOCIAL_TWITTER, 'Twitter'),
        (SOCIAL_MEDIUM, 'Medium'),
        (PERSONAL_WEBSITE, 'Website'),
        (SOCIAL_FACEBOOK, 'Facebook')
    )

    # ##
    # Domain name for INBOX app configuration
    # ##

    CONSULTANT_DOMAIN = 'consultant.exo.works'
    USER_DOMAIN = 'user.exo.works'

    # ##
    # Entity types
    # ##

    PERMS_USER_EDIT = 'user_edit_profile'
    PERMS_MARKETPLACE_FULL = 'view_marketplace_full'
    PERMS_MARKETPLACE_FULL_PERMISSION_REQUIRED = '{}.{}'.format(app_name, PERMS_MARKETPLACE_FULL)

    PERMS_EXQ_FULL = 'view_exq_full'
    PERMS_EXQ_FULL_PERMISSION_REQUIRED = '{}.{}'.format(app_name, PERMS_EXQ_FULL)

    PERMS_ACCESS_EXQ = 'exq_access'
    PERMS_ACCESS_EXO_PROJECTS = 'exo_projects_access'

    ALL_PERMISSIONS = (
        (PERMS_USER_EDIT, 'Edit User Profile'),
        (PERMS_MARKETPLACE_FULL, 'Can view Marketplace'),
        (PERMS_EXQ_FULL, 'Can view ExQ'),
        (PERMS_ACCESS_EXQ, 'Access to ExQ Tool'),
        (PERMS_ACCESS_EXO_PROJECTS, 'Access to ExO Projects'),
    )

    PROFILE_COLOR_BACKGROUND = (
        '#4DB6AC',
        '#5E97F6',
        '#90A4AE',
        '#A1887F',
        '#AED581',
        '#B39DDB',
        '#C5CD57',
        '#E897F6',
        '#F87165',
        '#EA80FC'
    )

    SMALL_IMAGE_SIZE = 24
    MEDIUM_IMAGE_SIZE = 48
    LARGE_IMAGE_SIZE = 96
    DEFAULT_IMAGE_SIZE = 144
    DEFAULT_PICTURES_SIZES = (
        (SMALL_IMAGE_SIZE, SMALL_IMAGE_SIZE),
        (MEDIUM_IMAGE_SIZE, MEDIUM_IMAGE_SIZE),
        (LARGE_IMAGE_SIZE, LARGE_IMAGE_SIZE),
        (DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE),
    )
    PROFILE_PICTURE_SIZES = DEFAULT_PICTURES_SIZES

    VALIDATION_CHOICES_VERIFIED = 'V'
    VALIDATION_CHOICES_NOT_VERIFIED = 'NV'
    VALIDATION_CHOICES_NOT_OWNER = 'X'      # Is not the email owner
    VALIDATION_CHOICES_OTHER_USER = 'O'
    VALIDATION_CHOICES_PENDING = 'P'
    VALIDATION_CHOICES_DISCARTED = 'D'

    EMAIL_VALIDATION = {
        VALIDATION_CHOICES_VERIFIED: 'Email account changed successfully',
        VALIDATION_CHOICES_NOT_VERIFIED: 'You have already added this email '
        'before, but it wasn\'t verified yet. Please check your email inbox',
        VALIDATION_CHOICES_NOT_OWNER: 'Sorry, this email does not exist',
        VALIDATION_CHOICES_OTHER_USER: 'Sorry, there is an user with this email'
        ' address. Please contact to support@openexo.com for more details.',
        VALIDATION_CHOICES_PENDING: 'We have sent an email to validate'
        ' this email account. Please, have a look to your inbox. ',
        VALIDATION_CHOICES_DISCARTED: 'You email has been discarted'
    }

    SEGMENT_CONSULTANT = 'Consultant'
    SEGMENT_CUSTOMER = 'Customer'
    SEGMENT_STAFF = 'Staff'

    CH_PERSONAL_EMAIL = 'P'
    CH_EXO_EMAIL = 'E'

    CH_TYPE_EMAIL = (
        (CH_PERSONAL_EMAIL, 'Personal'),
        (CH_EXO_EMAIL, 'ExO Email'),
    )

    # ##
    # Conf ExO Staff
    # ##

    PROFILE_PICTURE_CH_DEFAULT = 'D'
    PROFILE_PICTURE_CH_LINKEDIN = 'L'
    PROFILE_PICTURE_CH_USER = 'U'

    PROFILE_PICTURE_ORIGIN_CHOICES = (
        (PROFILE_PICTURE_CH_DEFAULT, 'Image default'),
        (PROFILE_PICTURE_CH_LINKEDIN, 'Image linkedin'),
        (PROFILE_PICTURE_CH_USER, 'Image from user')
    )

    # ##
    # Classes to detect empty users
    # ##

    EMPTY_USER_CLASSES = [
        ['exo_accounts', 'User'],
        ['exo_accounts', 'EmailAddress'],
    ]

    # ##
    # Intercom
    # ##

    REDIS_KEY_INTERCOM_HASH = 'intercom_hash'
    REDIS_KEY_PLATFORM_LANGUAGE = 'platform_language'

    # Sections available for visits

    MARKETPLACE_SECTION = 'marketplace'
    EXQ_SECTION = 'exq'

    SECTIONS_VISITED_AVAILABLE = [
        MARKETPLACE_SECTION,
        EXQ_SECTION,
    ]
