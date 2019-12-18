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


class RelationConfig(AppConf):
    APP_NAME = 'relation'

    # Permissions
    ACTIVE_ROLE = 'active_role'
    CANCEL_ROLE = 'cancel_role'
    ALL_PERMISSIONS = (
        (ACTIVE_ROLE, 'Can activate a role'),
        (CANCEL_ROLE, 'Can cancel a role'),
    )

    # Role status
    ROLE_CH_ACTIVE = 'A'
    ROLE_CH_INACTIVE = 'I'
    ROLE_CH_STATUS = (
        (ROLE_CH_ACTIVE, 'Active'),
        (ROLE_CH_INACTIVE, 'Inactive'),
    )

    # Base roles
    ROLE_CH_ADMIN = 'A'
    ROLE_CH_REGULAR = 'R'
    ROLE_CH_CONSULTANT = 'C'

    # Partner Roles
    PARTNER_CH_ROLE_DEFAULT = ROLE_CH_ADMIN
    PARTNER_CH_ROLE = (
        (ROLE_CH_ADMIN, 'Admin'),
        (ROLE_CH_REGULAR, 'Regular'),
        (ROLE_CH_CONSULTANT, 'Consultant'),
    )

    # Customer Roles
    CUSTOMER_CH_ROLE_DEFAULT = ROLE_CH_ADMIN

    CUSTOMER_CH_ROLE = (
        (ROLE_CH_ADMIN, 'Admin'),
        (ROLE_CH_REGULAR, 'Regular'),
    )

    # INTERNAL ORGANIZATION Roles
    ORGANIZATION_CH_ROLE_DEFAULT = ROLE_CH_ADMIN
    ORGANIZATION_CH_ROLE = (
        (ROLE_CH_ADMIN, 'Admin'),
        (ROLE_CH_REGULAR, 'Regular'),
    )

    # Partner - Customer Roles
    ROLE_CH_SALES = 'S'
    ROLE_CH_DELIVERY = 'D'
    ROLE_CH_ALL = 'A'
    PARTNER_CUSTOMER_CH_ROLE_DEFAULT = ROLE_CH_SALES
    PARTNER_CUSTOMER_CH_ROLE = (
        (ROLE_CH_SALES, 'Sales'),
        (ROLE_CH_DELIVERY, 'Delivery'),
        (ROLE_CH_ALL, 'All'),
    )

    # Industries
    INDUSTRIES_CHOICES = (
        (1, 'Intermediate'),
        (2, 'Advanced'),
        (3, 'Thought leader'),
    )

    # Atributes
    EXO_ATTRIBUTE_DEFAULT = 0
    EXO_ATTRIBUTE_CHOICES = (
        (0, "I haven't read about it"),
        (1, 'I have read about it and understand it'),
        (2, 'I have studied it in some detail'),
        (3, 'I have implemented this once or twice'),
        (4, 'I have implemented this several times'),
        (5, 'I’m considered a thought leader in this domain'),
    )

    # Keywords
    KEYWORD_CHOICES = (
        (3, 'Can inspire'),
        (2, 'Can teach'),
        (1, 'Can speak'),
    )
    MIN_KEYWORD_LEVEL = 1

    # ExO Activity
    ACTIVITY_STATUS_CH_ACTIVE = 'A'
    ACTIVITY_STATUS_CH_DISABLED = 'D'
    ACTIVITY_STATUS_CH_PENDING = 'P'
    ACTIVITY_STATUS_CH_DEFAULT = ACTIVITY_STATUS_CH_PENDING
    ACTIVITY_STATUS_CHOICES = (
        (ACTIVITY_STATUS_CH_ACTIVE, 'Enabled'),
        (ACTIVITY_STATUS_CH_DISABLED, 'Disabled'),
        (ACTIVITY_STATUS_CH_PENDING, 'Pending'),
    )
    ACTIVITY_ROLE = 'active_role'
    ACTIVITY_ALL_PERMISSIONS = (
        (ACTIVITY_ROLE, 'Can activate a role')
    )

    # Certification
    CONSULTANT_ROLE_GROUP_TYPE_AMBASSADOR = 'consultantrole-ambassador'
    CONSULTANT_ROLE_GROUP_TYPE_CONSULTANT = 'consultantrole-consultant'
    CONSULTANT_ROLE_GROUP_TYPE_FOUNDATIONS = 'consultantrole-foundations'
    CONSULTANT_ROLE_GROUP_TYPE_COACH = 'consultantrole-sprint-coach'
    CONSULTANT_ROLE_GROUP_TYPE_TRAINER = 'consultantrole-trainer'
    CONSULTANT_ROLE_GROUP_TYPE_EXO_TRAINER = 'consultantrole-exo-trainer'
    CONSULTANT_ROLE_GROUP_TYPE_ALIGN_TRAINER = 'consultantrole-align-trainer'
    CONSULTANT_ROLE_GROUP_TYPE_BOARD_ADVISOR = 'consultantrole-board-advisor'

    CONSULTANT_ROLE_GROUP_TYPE_CHOICES = (
        (CONSULTANT_ROLE_GROUP_TYPE_FOUNDATIONS, 'ExO Foundations'),
        (CONSULTANT_ROLE_GROUP_TYPE_CONSULTANT, 'ExO Consultant'),
        (CONSULTANT_ROLE_GROUP_TYPE_AMBASSADOR, 'ExO Ambassador'),
        (CONSULTANT_ROLE_GROUP_TYPE_COACH, 'ExO Sprint Coach'),
        (CONSULTANT_ROLE_GROUP_TYPE_TRAINER, 'ExO Workshop Trainer'),
        (CONSULTANT_ROLE_GROUP_TYPE_EXO_TRAINER, 'ExO Trainer'),
        (CONSULTANT_ROLE_GROUP_TYPE_ALIGN_TRAINER, 'ExO Align Trainer'),
        (CONSULTANT_ROLE_GROUP_TYPE_BOARD_ADVISOR, 'ExO Board Advisor'),
    )
