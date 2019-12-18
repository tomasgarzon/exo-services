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


class SprintAutomatedConfig(AppConf):
    APP_NAME = 'sprint_automated'

    CH_ACCOMPLISH_1 = '1'
    CH_ACCOMPLISH_2 = '2'
    CH_ACCOMPLISH_3 = '3'

    CH_ACCOMPLISH = (
        (CH_ACCOMPLISH_1, 'To reinvent the industry and transform our organization'),
        (CH_ACCOMPLISH_2, 'To transform our organization so that it’s able to adapt to external industry disruption'),
        (CH_ACCOMPLISH_3, 'To launch an ExO or multiple ExOs in order to transform the industry'),
    )

    CH_TRANSFORM_1 = '1'
    CH_TRANSFORM_2 = '2'
    CH_TRANSFORM_3 = '3'

    CH_TRANSFORM = (
        (CH_TRANSFORM_1, 'The organisation as a whole, including all markets and industries in which it is positioned'),
        (CH_TRANSFORM_2, 'A specific business unit focused on a particular industry'),
    )

    CH_PLAYGROUND_1 = '1'
    CH_PLAYGROUND_2 = '2'
    CH_PLAYGROUND_3 = '3'

    CH_PLAYGROUND = (
        (CH_PLAYGROUND_1, 'Any industry'),
        (CH_PLAYGROUND_2, 'Adjacent industries'),
        (CH_PLAYGROUND_3, 'Our current industry, with a goal of creating an ExO'),
    )

    STEPS_COUNT = 13

    STEP_INDEX_FEEDBACK_START = 4
    STEP_INDEX_FEEDBACK_END = 13

    STEP_INDEX_MICROLEARNING_START = 4
    STEP_INDEX_MICROLEARNING_END = 13

    ADD_SPRINT = 'add_sprintautomated'
    FULL_ADD_SPRINT = '{}.{}'.format(APP_NAME, ADD_SPRINT)
