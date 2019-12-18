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


class LearningConfig(AppConf):
    APP_NAME = 'learning'

    ADD_RESOURCE_PERMS = 'add_resource'
    CHANGE_RESOURCE_PERMS = 'change_resource'
    DELETE_RESOURCE_PERMS = 'delete_resource'

    LIST_RESOURCE_PERMS = 'list_resource'

    ALL_RESOURCE_PERMS = (
        (LIST_RESOURCE_PERMS, 'List resources'),
    )

    FULL_LIST_RESOURCE_PERMS = '{}.{}'.format(APP_NAME, LIST_RESOURCE_PERMS)
    FULL_ADD_RESOURCE_PERMS = '{}.{}'.format(APP_NAME, ADD_RESOURCE_PERMS)
    FULL_CHANGE_RESOURCE_PERMS = '{}.{}'.format(APP_NAME, CHANGE_RESOURCE_PERMS)
    FULL_DELETE_RESOURCE_PERMS = '{}.{}'.format(APP_NAME, DELETE_RESOURCE_PERMS)

    USER_MICROLEARNING_TYPEFORM_PARAM = 'object_id'
    USER_MICROLEARNING_STATUS_NONE = 'N'
    USER_MICROLEARNING_STATUS_PENDING = 'P'
    USER_MICROLEARNING_STATUS_DONE = 'D'

    USER_MICROLEARNING_STATUS_CHOICES = (
        (USER_MICROLEARNING_STATUS_NONE, 'Not available'),
        (USER_MICROLEARNING_STATUS_PENDING, 'Pending'),
        (USER_MICROLEARNING_STATUS_DONE, 'Done'),
    )
