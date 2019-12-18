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


class PartnerConfig(AppConf):
    # Entity types
    APP_NAME = 'partner'

    EDIT_PARTNER = 'partner_edit'
    ADD_PARTNER = 'add_partner'
    ADD_USER = 'partner_add_user'
    DELETE_USER = 'partner_delete_user'
    VIEW_PARTNER = 'partner_view'
    REMOVE_PARTNER = 'partner_remove'
    LIST_PARTNER = 'list_partner'

    ADMIN_PERMISSIONS = (
        EDIT_PARTNER,
        ADD_USER,
        DELETE_USER,
        ADD_PARTNER,
    )

    REGULAR_PERMISSIONS = (
        VIEW_PARTNER,
    )

    ALL_ADMIN_PERMISSIONS = (
        (EDIT_PARTNER, 'Edit Partner information'),
        (ADD_USER, 'Add user role'),
        (DELETE_USER, 'Delete user role'),
        (REMOVE_PARTNER, 'Remove Partner'),
    )

    ALL_REGULAR_PERMISSIONS = (
        (VIEW_PARTNER, 'View General Partner information'),
    )

    ALL_STAFF_PERMISSIONS = (
        (LIST_PARTNER, 'List partner'),
    )

    ALL_PERMISSIONS = ALL_ADMIN_PERMISSIONS + ALL_REGULAR_PERMISSIONS + ALL_STAFF_PERMISSIONS

    FULL_VIEW_PARTNER = '{}.{}'.format(APP_NAME, VIEW_PARTNER)
    FULL_LIST_PARTNER = '{}.{}'.format(APP_NAME, LIST_PARTNER)
    FULL_ADD_PARTNER = '{}.{}'.format(APP_NAME, ADD_PARTNER)
    FULL_EDIT_PARTNER = '{}.{}'.format(APP_NAME, EDIT_PARTNER)
    FULL_REMOVE_PARTNER = '{}.{}'.format(APP_NAME, REMOVE_PARTNER)
