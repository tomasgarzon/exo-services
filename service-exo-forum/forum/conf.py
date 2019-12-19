import logging

# 3rd. libraries imports
from appconf import AppConf

# django imports
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class ForumConfig(AppConf):
    APP_NAME = 'forum'

    ACTION_CREATE_POST = 'create'
    ACTION_EDIT_POST = 'edit-post'
    ACTION_RATING_POST = 'rating-post'
    ACTION_UP_VOTE = 'up'
    ACTION_DOWN_VOTE = 'down'
    ACTION_REPLY_POST = 'reply'
    ACTION_RATING_ANSWER = 'rating-answer'
    ACTION_EDIT_ANSWER = 'edit-answer'
    ACTION_REMOVE = 'remove'

    PERMS_EDIT_POST = 'edit_post'
    PERMS_EDIT_ANSWER = 'edit_answer'

    PERMS_POST_ALL_PERMISSIONS = (
        (PERMS_EDIT_POST, 'Edit Post'),
    )

    PERMS_ANSWER_ALL_PERMISSIONS = (
        (PERMS_EDIT_ANSWER, 'Edit Answer'),
    )

    CH_DRAFT = 'D'
    CH_PUBLISHED = 'P'
    CH_REMOVED = 'R'
    CH_BLOCKED = 'B'

    CH_POST_STATUS_DEFAULT = CH_PUBLISHED

    CH_POST_STATUS = (
        (CH_DRAFT, 'Draft'),
        (CH_PUBLISHED, 'Published'),
        (CH_REMOVED, 'Removed'),
        (CH_BLOCKED, 'Blocked'),
    )

    NOTIFICATION_ACTION_CREATE = 'create'
    NOTIFICATION_ACTION_UPDATE = 'update'
    NOTIFICATION_ACTION_DELETE = 'delete'

    # Category Types
    CATEGORY_CH_TYPE_OPEN = 'O'
    CATEGORY_CH_TYPE_PUBLIC = 'P'
    CATEGORY_CH_TYPE_SECRET = 'S'
    CATEGORY_CH_TYPE_CERTIFIED = 'C'

    CATEGORY_CH_TYPES = (
        (CATEGORY_CH_TYPE_OPEN, 'Open'),
        (CATEGORY_CH_TYPE_PUBLIC, 'Public'),
        (CATEGORY_CH_TYPE_SECRET, 'Private'),
        (CATEGORY_CH_TYPE_CERTIFIED, 'Certified'),
    )

    PERMS_CREATE_POST = 'create_post'

    CATEGORY_ALL_PERMISSIONS = (
        (PERMS_CREATE_POST, 'Create post'),
    )
