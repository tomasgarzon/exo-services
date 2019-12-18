from __future__ import absolute_import, unicode_literals

import logging

from appconf import AppConf

from django.conf import settings  # noqa

from exo_role.conf import settings as exo_role_settings


logger = logging.getLogger(__name__)


class EventConfig(AppConf):

    APP_NAME = 'event'

    MANAGE_URL = '/ecosystem/events/review/'
    DETAIL_URL = '/ecosystem/events/details/'

    EVENT_LOGO_COLOR_BACKGROUND = (
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
    EVENT_LOGO_SIZES = ((32, 32), (56, 56), (96, 96), (150, 150))

    TYPE_CHOICES = (
        (exo_role_settings.EXO_ROLE_CATEGORY_TALK, 'OpenExO Talk'),
        (exo_role_settings.EXO_ROLE_CATEGORY_WORKSHOP, 'OpenExO Workshop'),
        (exo_role_settings.EXO_ROLE_CATEGORY_SUMMIT, 'OpenExO Summit'),
        (exo_role_settings.EXO_ROLE_CATEGORY_OTHER, 'Other'),
    )

    CH_STATUS_PENDING = 'P'
    CH_STATUS_UNDER_REVIEW = 'R'
    CH_STATUS_PUBLIC = 'H'
    CH_STATUS_DELETED = 'D'
    CH_STATUS_DEFAULT = CH_STATUS_PENDING
    STATUS_CHOICES = (
        (CH_STATUS_PENDING, 'Pending'),
        (CH_STATUS_UNDER_REVIEW, 'Under review'),
        (CH_STATUS_PUBLIC, 'Public'),
        (CH_STATUS_DELETED, 'Deleted'),
    )

    CH_FOLLOW_MODE_ON_SITE = 'P'
    CH_FOLLOW_MODE_STREAMING = 'S'
    CH_FOLLOW_MODE_VIRTUAL = 'V'
    CH_FOLLOW_MODE_DEFAULT = CH_FOLLOW_MODE_ON_SITE
    FOLLOW_MODE_CHOICES = (
        (CH_FOLLOW_MODE_ON_SITE, 'On Site'),
        (CH_FOLLOW_MODE_STREAMING, 'Streaming'),
        (CH_FOLLOW_MODE_VIRTUAL, 'Virtual'),
    )

    CH_CURRENCY_EUR = 'E'
    CH_CURRENCY_DOL = 'D'
    CH_CURRENCY_DEFAULT = CH_CURRENCY_EUR
    CURRENCY_CHOICES = (
        (CH_CURRENCY_EUR, '€'),
        (CH_CURRENCY_DOL, '$'),
    )
    PRICE_STR_E = '%(amount)s %(currency)s'
    PRICE_STR_D = '%(currency)s%(amount)s'

    SPEAKER_NAME = 'Speaker'
    PARTICIPANT_NAME = 'Participant'
    TRAINER_NAME = 'Trainer'
    COLLABORATOR_NAME = 'Collaborator'
    FACILITATOR_NAME = 'Facilitator'
    ORGANIZER_NAME = 'Organizer'
    COACH_NAME = 'Coach'

    PARTICIPANT_ROLE_CHOICES = {
        exo_role_settings.EXO_ROLE_CATEGORY_TALK: (
            (exo_role_settings.EXO_ROLE_CODE_TALK_PARTICIPANT, PARTICIPANT_NAME),
            (exo_role_settings.EXO_ROLE_CODE_TALK_SPEAKER, SPEAKER_NAME),
        ),
        exo_role_settings.EXO_ROLE_CATEGORY_WORKSHOP: (
            (exo_role_settings.EXO_ROLE_CODE_WORKSHOP_PARTICIPANT, PARTICIPANT_NAME),
            (exo_role_settings.EXO_ROLE_CODE_WORKSHOP_SPEAKER, SPEAKER_NAME),
            (exo_role_settings.EXO_ROLE_CODE_WORKSHOP_TRAINER, TRAINER_NAME),
        ),
        exo_role_settings.EXO_ROLE_CATEGORY_SUMMIT: (
            (exo_role_settings.EXO_ROLE_CODE_SUMMIT_PARTICIPANT, PARTICIPANT_NAME),
            (exo_role_settings.EXO_ROLE_CODE_SUMMIT_COLLABORATOR, COLLABORATOR_NAME),
            (exo_role_settings.EXO_ROLE_CODE_SUMMIT_SPEAKER, SPEAKER_NAME),
            (exo_role_settings.EXO_ROLE_CODE_SUMMIT_FACILITATOR, FACILITATOR_NAME),
            (exo_role_settings.EXO_ROLE_CODE_SUMMIT_ORGANIZER, ORGANIZER_NAME),
            (exo_role_settings.EXO_ROLE_CODE_SUMMIT_COACH, COACH_NAME),
        ),
        exo_role_settings.EXO_ROLE_CATEGORY_OTHER: (
            (exo_role_settings.EXO_ROLE_CODE_OTHER_PARTICIPANT, PARTICIPANT_NAME),
            (exo_role_settings.EXO_ROLE_CODE_OTHER_SPEAKER, SPEAKER_NAME),
        )
    }

    CH_ROLE_STATUS_ACTIVE = 'A'
    CH_ROLE_STATUS_DELETED = 'D'
    CH_ROLE_STATUS_PENDING = 'P'
    CH_ROLE_STATUS_DEFAULT = CH_ROLE_STATUS_ACTIVE
    ROLE_STATUS_CHOICES = (
        (CH_ROLE_STATUS_ACTIVE, 'Active'),
        (CH_ROLE_STATUS_DELETED, 'Deleted'),
        (CH_ROLE_STATUS_PENDING, 'Pending'),
    )

    # ##
    # Permissions
    # ##

    PERMS_EDIT_EVENT = 'edit-event'
    PERMS_DELETE_EVENT = 'delete-event'
    PERMS_MANAGE_EVENT = 'manage-event'
    PERMS_CREATE_EVENT_SUMMIT = 'create-event-summit'
    ALL_PERMISSIONS = (
        (PERMS_EDIT_EVENT, 'Edit Event'),
        (PERMS_DELETE_EVENT, 'Delete Event'),
        (PERMS_MANAGE_EVENT, 'Manage Event'),
        (PERMS_CREATE_EVENT_SUMMIT, 'Create Event Summit'),
    )
    ALL_PERMISSIONS = ALL_PERMISSIONS
    FULL_PERMS_MANAGE_EVENT = '{}.{}'.format(APP_NAME, PERMS_MANAGE_EVENT)
    FULL_PERMS_CREATE_EVENT_SUMMIT = '{}.{}'.format(APP_NAME, PERMS_CREATE_EVENT_SUMMIT)

    AMBASSADOR_CERTIFICATION_CODE = exo_role_settings.EXO_ROLE_CODE_CERTIFICATION_AMBASSADOR
    COACH_CERTIFICATION_CODE = exo_role_settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH
    FOUNDATIONS_CERTIFICATION_CODE = exo_role_settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS
    TRAINER_CERTIFICATION_CODE = exo_role_settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER

    PERMMISIONS = {
        exo_role_settings.EXO_ROLE_CATEGORY_TALK: [
            AMBASSADOR_CERTIFICATION_CODE,
            COACH_CERTIFICATION_CODE,
            FOUNDATIONS_CERTIFICATION_CODE,
            TRAINER_CERTIFICATION_CODE,
        ],
        exo_role_settings.EXO_ROLE_CATEGORY_WORKSHOP: [
            TRAINER_CERTIFICATION_CODE,
        ],
        exo_role_settings.EXO_ROLE_CATEGORY_SUMMIT: [],
        exo_role_settings.EXO_ROLE_CATEGORY_OTHER: [],
    }

    CREATION_WORKSHOP_REMINDER_RECIPIENTS = [
        'marketing@openexo.com',
        'scarletta@openexo.com',
        'service@openexo.com',
    ]
    SUMMIT_DISTRIBUTION_LIST_EMAIL = 'summits@openexo.com'

    SUMMITS_SIGNUPS_ENTRY_POINT = 'SUMMITS_SIGNUPS'
