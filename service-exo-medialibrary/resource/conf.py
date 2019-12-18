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


class ResourceConfig(AppConf):

    CH_TYPE_VIDEO_VIMEO = 'V'
    CH_TYPE_VIDEO_YOUTUBE = 'Y'
    CH_TYPE_VIDEO_DRIVE = 'D'
    CH_TYPE_VIDEO_DROPBOX = 'X'
    CH_TYPE_FILESTACK = 'F'

    CH_TYPES = (
        (CH_TYPE_VIDEO_VIMEO, 'Video Vimeo'),
        (CH_TYPE_VIDEO_YOUTUBE, 'Video Youtube'),
        (CH_TYPE_VIDEO_DRIVE, 'Video Drive'),
        (CH_TYPE_VIDEO_DROPBOX, 'Video Dropbox'),
        (CH_TYPE_FILESTACK, 'Filestack'),
    )

    VIDEO_DEFAULT_WIDTH = "100%"
    VIDEO_DEFAULT_HEIGHT = "100%"

    CH_STATUS_DRAFT = 'D'
    CH_STATUS_AVAILABLE = 'A'
    CH_STATUS_ERROR = 'E'
    CH_STATUS_REMOVED = 'R'

    CH_STATUS = (
        (CH_STATUS_DRAFT, 'Draft'),
        (CH_STATUS_AVAILABLE, 'Available'),
        (CH_STATUS_ERROR, 'Error'),
        (CH_STATUS_REMOVED, 'Removed')
    )

    PROVIDER_STATUS_AVAILABLE = 'available'
    PROVIDER_STATUS_UPLOADING_ERROR = 'uploading_error'

    PROVIDERS_STATUS = {
        PROVIDER_STATUS_AVAILABLE: CH_STATUS_AVAILABLE,
        PROVIDER_STATUS_UPLOADING_ERROR: CH_STATUS_ERROR,
    }

    DEVELOPMENT_TAGS_COUNT = 1
    DEVELOPMENT_TAG_NAME = 'dev-tag'

    PERMISSION_ADD_RESOURCE = 'add_resource'
    PERMISSION_CHANGE_RESOURCE = 'change_resource'
    PERMISSION_DELETE_RESOURCE = 'delete_resource'

    ADMIN_PERMISSIONS = [
        PERMISSION_ADD_RESOURCE,
        PERMISSION_CHANGE_RESOURCE,
        PERMISSION_DELETE_RESOURCE
    ]

    UPLOAD_CHANNEL_NAME = 'video-upload'
    UPLOAD_WEBSOCKET_GROUP_NAME = 'events'

    CH_SECTION_SPRINT = 'S'
    CH_SECTION_SPRINT_AUTOMATED = 'A'
    CH_SECTION_WORKSHOP = 'W'
    CH_SECTION_FASTRACKSPRINT = 'F'
    CH_SECTION_ECOSYSTEM = 'E'
    CH_SECTION_SPEAKERS = 'P'
    CH_SECTION_TRAINERS = 'T'
    CH_SECTION_CONSULTANTS = 'C'
    CH_SECTION_COACHES = 'O'
    CH_SECTION_ALUMNI = 'L'
    CH_SECTION_DELIVERY_AND_PARTNER = 'D'
    CH_SECTION_DEFAULT = CH_SECTION_SPRINT_AUTOMATED

    CH_SECTIONS = (
        (CH_SECTION_SPRINT, 'Sprint'),
        (CH_SECTION_SPRINT_AUTOMATED, 'Sprint Automated'),
        (CH_SECTION_WORKSHOP, 'Workshop'),
        (CH_SECTION_FASTRACKSPRINT, 'Fastrack'),
        (CH_SECTION_ECOSYSTEM, 'Ecosystem'),
        (CH_SECTION_SPEAKERS, 'Speakers'),
        (CH_SECTION_TRAINERS, 'Trainers'),
        (CH_SECTION_CONSULTANTS, 'Consultants'),
        (CH_SECTION_COACHES, 'Coaches'),
        (CH_SECTION_ALUMNI, 'Alumni'),
        (CH_SECTION_DELIVERY_AND_PARTNER, 'Delivery and partner'),
    )

    CH_TYPE_SPRINT = 'sprint'
    CH_TYPE_SPRINT_AUTOMATED = 'sprintautomated'
    CH_TYPE_WORKSHOP = 'workshop'
    CH_TYPE_FASTRACKSPRINT = 'fastracksprint'

    CH_TYPE_PROJECT = (
        (CH_TYPE_SPRINT, CH_TYPE_SPRINT),
        (CH_TYPE_SPRINT_AUTOMATED, CH_TYPE_SPRINT_AUTOMATED),
        (CH_TYPE_WORKSHOP, CH_TYPE_WORKSHOP),
        (CH_TYPE_FASTRACKSPRINT, CH_TYPE_FASTRACKSPRINT),
    )

    RELATION_TYPES_AND_SECTIONS = {
        CH_TYPE_SPRINT: CH_SECTION_SPRINT,
        CH_TYPE_SPRINT_AUTOMATED: CH_SECTION_SPRINT_AUTOMATED,
        CH_TYPE_WORKSHOP: CH_SECTION_WORKSHOP,
        CH_TYPE_FASTRACKSPRINT: CH_SECTION_FASTRACKSPRINT,
    }

    FILESTACK_CDN_URL = 'cdn.filestackcontent.com'

    CH_MESSAGE_DEBUG = 10
    CH_MESSAGE_INFO = 20
    CH_MESSAGE_SUCCESS = 25
    CH_MESSAGE_WARNING = 30
    CH_MESSAGE_ERROR = 40

    CH_CODE_MESSAGE_UPLOAD = 'R'
