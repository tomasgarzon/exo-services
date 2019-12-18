# python imports
import logging

# 3rd. libraries imports
from appconf import AppConf

# django imports
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class BadgeConfig(AppConf):
    APP_NAME = 'badge'

    # Community
    CODE_CONTENT_CREATOR = 'CCC'
    CODE_COMMUNITY_BUILDER = 'CCB'
    CODE_COMMUNITY_CHOICES = (
        (CODE_CONTENT_CREATOR, 'Content Creator'),
        (CODE_COMMUNITY_BUILDER, 'Community Builder'),
    )

    CODE_CHOICES = list(CODE_COMMUNITY_CHOICES) \
        + list(settings.EXO_ROLE_CODE_CHOICES)

    CATEGORY_COMMUNITY = 'CC'

    # Category
    CATEGORY_CHOICES = [
        (CATEGORY_COMMUNITY, 'Community'),
    ] + list(settings.EXO_ROLE_CATEGORY_CODE_CHOICES)

    # ACTSTREAM
    ACTION_LOG_CREATE = 'badge-create'
    ACTION_LOG_UPDATE = 'badge-update'
    ACTION_LOG_DELETE = 'badge-delete'
    ACTSTREAM_ACTIONS = (
        (ACTION_LOG_CREATE, 'Badge created'),
        (ACTION_LOG_UPDATE, 'Badge updated'),
        (ACTION_LOG_DELETE, 'Badge deleted'),
    )

    ACTION_LOG_CREATE_SIGNAL_DESCRIPTION = 'signal'

    # Permissions
    PERMISSION_ADD_BADGE = 'add_userbadge'
    FULL_PERMISSION_ADD_BADGE = '{}.{}'.format(APP_NAME, PERMISSION_ADD_BADGE)
