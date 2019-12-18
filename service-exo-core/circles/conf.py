# python imports
import logging

# 3rd. libraries imports
from appconf import AppConf

# django imports
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class CirclesConfig(AppConf):
    PERMS_CREATE_POST = 'create_post'

    ALL_PERMISSIONS = (
        (PERMS_CREATE_POST, 'Create post'),
    )

    ECOSYSTEM_NAME = 'Community'
    FEEDBACK_NAME = 'Platform Feedback'
    CONSULTANTS_NAME = 'Consultants'

    FOR_CONSULTANTS = [
        ECOSYSTEM_NAME,
    ]

    PROJECT_QUESTION_CIRCLE_NAME = 'questions'

    # ##
    # Metrics
    # ##

    METRIC_ACTIONS_LIST = (
        ('started following', 'Follow Circle'),
        ('stopped following', 'Unfollow Circle'),
    )

    # Circle Types
    CH_TYPE_OPEN = 'O'
    CH_TYPE_PUBLIC = 'P'
    CH_TYPE_SECRET = 'S'
    CH_TYPE_CERTIFIED = 'C'

    CH_TYPES = (
        (CH_TYPE_OPEN, 'Open'),
        (CH_TYPE_PUBLIC, 'Public'),
        (CH_TYPE_SECRET, 'Private'),
        (CH_TYPE_CERTIFIED, 'Certified'),
    )

    # Circles filter params
    PARAM_STATUS_CH_SUBSCRIBED = 'S'
    PARAM_STATUS_CH_NOT_SUBSCRIBED = 'U'

    # User circle status
    CH_USER_STATUS_GUEST = 'G'
    CH_USER_STATUS_MEMBER = 'M'

    CH_USER_STATUSES = (
        (CH_USER_STATUS_GUEST, 'Guest'),
        (CH_USER_STATUS_MEMBER, 'Member'),
    )

    # Circles information
    SLUG_ALUMNI = 'alumni'
    SLUG_AMBASSADORS = 'ambassadors'
    SLUG_COACHES = 'coaches'
    SLUG_CONSULTANTS = 'consultants'
    SLUG_ECOSYSTEM = 'ecosystem'
    SLUG_EXT_BOOK_COLLABORATORS = 'ext-book-collaborators'
    SLUG_INVESTORS = 'investors'
    SLUG_TRAINERS = 'trainers'

    CIRCLE_DESCRIPTIONS = (
        (SLUG_ALUMNI, 'This is a private group for alumni from previous ExO projects to share experiences and continue working on the transformation journey. Feel free to create new posts to discuss topics and share resources and insights'),  # noqa
        (SLUG_AMBASSADORS, 'This is a private group where ExO Ambassadors can create posts, respond to topics of interest, collaborate and share resources and insights'),  # noqa
        (SLUG_COACHES, 'This is a private group where ExO Coaches and ExO Head Coaches can create posts, respond to topics of interest, collaborate and share resources and insights'),  # noqa
        (SLUG_CONSULTANTS, 'This is a private group where ExO Consultants can create posts, respond to topics of interest, collaborate and share resources and insights'),  # noqa
        (SLUG_ECOSYSTEM, 'This is a community space where all ExO Ecosystem members can create posts, respond to topics of interest, collaborate and share resources and insights'),  # noqa
        (SLUG_EXT_BOOK_COLLABORATORS, 'This is a private feedback group where all ExO members who helped to shape, form and write the Exponential Transformations book can discuss and provide feedback on how to make the book even better'),  # noqa
        (SLUG_INVESTORS, 'This is a private group where ExO Investors can create posts, respond to topics of interest, collaborate and share resources and insights'),  # noqa
        (SLUG_TRAINERS, 'This is a private group where ExO Trainers can create posts, respond to topics of interest, collaborate and share resources and insights'),  # noqa
    )

    #  Certified circles
    CERTIFIED_CIRCLE_SLUGS = [
        SLUG_AMBASSADORS,
        SLUG_COACHES,
        SLUG_CONSULTANTS,
        SLUG_TRAINERS,
    ]

    #  Virtual circles
    ANNOUNCEMENT_NAME = 'Announcements'
    ANNOUNCEMENT_SLUG = 'announcements'
    ANNOUNCEMENT_IMAGE = 'https://cdn.filestackcontent.com/9GJ117GSQpeA5v5exlIh'
    ANNOUNCEMENT_DESCRIPTION = 'This is a community news space where OpenExO sends information to all ExO Ecosystem members on updates, new releases, events and experiments'  # noqa

    QUESTIONS_PROJECTS_NAME = 'Questions from Participants'
    QUESTIONS_PROJECTS_SLUG = 'participant-questions'
    QUESTIONS_PROJECTS_IMAGE = 'https://cdn.filestackcontent.com/kk8jh66hTIe4FsWSZfs8'
    QUESTIONS_PROJECTS_DESCRIPTION = 'This is a private group where ExO Community members interested in consulting can help current ExO Transformation Project teams with their questions. Feel free to answer the questions you are most comfortable addressing'  # noqa
