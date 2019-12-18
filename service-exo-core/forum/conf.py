import logging
import os

# 3rd. libraries imports
from appconf import AppConf

# django imports
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class ForumConfig(AppConf):
    APP_NAME = 'forum'

    TOPIC_DEFAULT = 'forum'
    TOPIC_SWARM = 'swarm'

    CH_CIRCLE = 'C'
    CH_QA_SESSION = 'Q'
    CH_PROJECT = 'P'
    CH_ANNOUNCEMENT = 'A'

    POST_CH_TYPE = (
        (CH_CIRCLE, 'Circle'),
        (CH_QA_SESSION, 'Q-A Session'),
        (CH_PROJECT, 'Project'),
        (CH_ANNOUNCEMENT, 'Announcement'),
    )

    ACTION_CREATE_POST = 'create'
    ACTION_EDIT_POST = 'edit-post'
    ACTION_RATING_POST = 'rating-post'
    ACTION_UP_VOTE = 'up'
    ACTION_DOWN_VOTE = 'down'
    ACTION_REPLY_POST = 'reply'
    ACTION_RATING_ANSWER = 'rating-answer'
    ACTION_EDIT_ANSWER = 'edit-answer'
    ACTION_NOTIFY_COACH = 'notify_coach'
    ACTION_REMOVE = 'remove'

    PERMS_EDIT_POST = 'edit_post'
    PERMS_EDIT_ANSWER = 'edit_answer'

    PERMS_POST_ALL_PERMISSIONS = (
        (PERMS_EDIT_POST, 'Edit Post'),
    )

    PERMS_ANSWER_ALL_PERMISSIONS = (
        (PERMS_EDIT_ANSWER, 'Edit Answer'),
    )

    TITLE_DEFAULT = 'Question title'

    ACTION_ROL_TEAM = 'T'
    ACTION_ROL_COACH = 'C'
    ACTION_ROL_ADVISOR = 'A'
    ACTION_ROL_CONSULTANT = 'L'
    ACTION_ROL_MANAGER = 'M'
    ACTION_ROL_STAFF = 'S'

    CREATED_ROL_NAME = (
        (ACTION_ROL_TEAM, 'Team Member'),
        (ACTION_ROL_COACH, 'ExO Coach'),
        (ACTION_ROL_ADVISOR, 'ExO Advisor'),
        (ACTION_ROL_CONSULTANT, 'ExO Consultant'),
        (ACTION_ROL_MANAGER, 'Head Coach'),
        (ACTION_ROL_STAFF, 'Staff'),
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

    NEW_POST_DELAY = int(os.environ.get('EMAIL_NEW_POST_DELAY', '600'))
    NEW_POST_QA_SESSION_DELAY = 1

    # Metrics
    # ##

    METRIC_CATEGORIES = {
        CH_ANNOUNCEMENT: 'Announcement',
        CH_CIRCLE: 'Circle',
        CH_QA_SESSION: 'SWARM Session',
        CH_PROJECT: 'Project Post',
    }

    METRIC_ACTIONS_LIST = (
        (ACTION_CREATE_POST, 'Create Topic'),
        (ACTION_EDIT_POST, 'Edit Topic'),
        (ACTION_REPLY_POST, 'Reply Topic'),
        (ACTION_EDIT_ANSWER, 'Edit Reply'),
        (ACTION_REMOVE, 'Remove'),
    )

    NOTIFICATION_ACTION_CREATE = 'create'
    NOTIFICATION_ACTION_UPDATE = 'update'
    NOTIFICATION_ACTION_DELETE = 'delete'
