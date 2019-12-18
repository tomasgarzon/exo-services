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


class CustomerConfig(AppConf):

    APP_NAME = 'customer'

    EDIT_CUSTOMER = 'edit_customer'
    ADD_CUSTOMER = 'add_customer'
    ADD_USER = 'add_user'
    VIEW_CUSTOMER = 'view_customer'
    REMOVE_CUSTOMER = 'remove_customer'
    LIST_CUSTOMER = 'list_customer'

    ADMIN_PERMISSIONS = (
        EDIT_CUSTOMER,
        ADD_USER,
    )

    REGULAR_PERMISSIONS = (
        VIEW_CUSTOMER,
    )

    ALL_ADMIN_PERMISSIONS = (
        (EDIT_CUSTOMER, 'Edit Customer information'),
        (ADD_USER, 'Add user role'),
        (REMOVE_CUSTOMER, 'Remove Customer'),
    )

    ALL_REGULAR_PERMISSIONS = (
    )

    ALL_STAFF_PERMISSIONS = (
        (LIST_CUSTOMER, 'List customer'),
    )

    ALL_PERMISSIONS = ALL_ADMIN_PERMISSIONS + ALL_REGULAR_PERMISSIONS + ALL_STAFF_PERMISSIONS

    IMAGE_CHOICES_PROFILE = (
        ('theme/gallery/1.jpg', 'Image1.jpg'),
    )

    FULL_LIST_CUSTOMER = '{}.{}'.format(APP_NAME, LIST_CUSTOMER)
    FULL_EDIT_CUSTOMER = '{}.{}'.format(APP_NAME, EDIT_CUSTOMER)
    FULL_VIEW_CUSTOMER = '{}.{}'.format(APP_NAME, VIEW_CUSTOMER)
    FULL_REMOVE_CUSTOMER = '{}.{}'.format(APP_NAME, REMOVE_CUSTOMER)
    FULL_ADD_CUSTOMER = '{}.{}'.format(APP_NAME, ADD_CUSTOMER)

    CH_TRAINING = 'T'
    CH_NORMAL = 'N'

    CH_TYPE_CUSTOMER = (
        (CH_NORMAL, 'Normal'),
        (CH_TRAINING, 'Training'),
    )
