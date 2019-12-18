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


class EntityConfig(AppConf):

    CH_ORGANIZATION_SIZE = (
        ('1', 'Small: 1-10 staff'),
        ('2', 'Medium: 11-100 staff'),
        ('3', 'Large: 100-500'),
        ('4', 'Very large: 500+'),
    )
