# python 3 imports
from __future__ import absolute_import, unicode_literals

# python imports
import logging

# 3rd. libraries imports
from appconf import AppConf

# django imports
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class MarketplaceConfig(AppConf):
    GROUP_NAME = 'marketplace'

    CH_STATUS_REQUEST = 'R'
    CH_STATUS_FINISHED = 'F'
    CH_STATUS_DEFAULT = CH_STATUS_REQUEST

    CH_STATUS = (
        (CH_STATUS_REQUEST, 'Requested'),
        (CH_STATUS_FINISHED, 'Finished'),
    )

    CH_PARTICIPANT_COMPANY = 'C'
    CH_PARTICIPANT_GOVERNMENT = 'G'
    CH_PARTICIPANT_INDIVIDUAL = 'I'
    CH_PARTICIPANT_DEFAULT = CH_PARTICIPANT_COMPANY

    CH_PARTICIPANT = (
        (CH_PARTICIPANT_COMPANY, 'Company'),
        (CH_PARTICIPANT_GOVERNMENT, 'Government Institution'),
        (CH_PARTICIPANT_INDIVIDUAL, 'Individual'),
    )

    CH_MOTIVATION_1 = '1'
    CH_MOTIVATION_2 = '2'
    CH_MOTIVATION_3 = '3'
    CH_MOTIVATION_4 = '4'
    CH_MOTIVATION_5 = '5'
    CH_MOTIVATION_6 = '6'
    CH_MOTIVATION_7 = '7'
    CH_MOTIVATION_8 = '8'
    CH_MOTIVATION_9 = '9'
    CH_MOTIVATION_DEFAULT = CH_MOTIVATION_1

    CH_MOTIVATION = (
        (CH_MOTIVATION_1, 'Finding the right business model that connects you to an economy of abundance rather than scarcity'),    # noqa
        (CH_MOTIVATION_2, 'Shifting the mindset of our organization from efficiency-based thinking to a focus on innovation'),      # noqa
        (CH_MOTIVATION_3, 'Build and retain innovation capacity within your organization'),     # noqa
        (CH_MOTIVATION_4, 'Neutralize your organizational immune system'),
        (CH_MOTIVATION_5, 'Access knowledge from outside your organization'),
        (CH_MOTIVATION_6, 'Practice using the processes, tools and techniques required for your organization to keep pace'),    # noqa
        (CH_MOTIVATION_7, 'Change your culture through personal and professional transformation'),  # noqa
        (CH_MOTIVATION_8, 'Predict the future by creating it'),
        (CH_MOTIVATION_9, 'Other'),
    )

    CH_GOAL_GUIDED_SPRINT = 'G'
    CH_GOAL_SELF_GUIDED_SPRINT = 'S'
    CH_GOAL_SPRINT_TEAM_PERSON = 'T'
    CH_GOAL_SPRINT_TEAM_REMOTE = 'R'
    CH_GOAL_ONLINE_SPRINT_COURSE = 'C'
    CH_GOAL_DEFAULT = CH_GOAL_GUIDED_SPRINT

    CH_GOAL = (
        (CH_GOAL_GUIDED_SPRINT, 'To be guided in my Sprint process'),
        (CH_GOAL_SELF_GUIDED_SPRINT, 'To guide myself or run a self guided in-house Sprint'),   # noqa
        (CH_GOAL_SPRINT_TEAM_PERSON, 'A sprint team in person'),
        (CH_GOAL_SPRINT_TEAM_REMOTE, 'A sprint team through online remote access'),     # noqa
        (CH_GOAL_ONLINE_SPRINT_COURSE, 'Access to the online Sprint course and video content'),     # noqa
    )

    CH_EMPLOYEES_RANGE_1 = '1'
    CH_EMPLOYEES_RANGE_2 = '2'
    CH_EMPLOYEES_RANGE_3 = '3'
    CH_EMPLOYEES_RANGE_4 = '4'
    CH_EMPLOYEES_RANGE_DEFAULT = CH_EMPLOYEES_RANGE_1

    CH_EMPLOYEES_RANGE = (
        (CH_EMPLOYEES_RANGE_1, '0-50'),
        (CH_EMPLOYEES_RANGE_2, '51-200'),
        (CH_EMPLOYEES_RANGE_3, '201-800'),
        (CH_EMPLOYEES_RANGE_4, '800+'),
    )

    CH_INITIATIVES_RANGE_1 = '1'
    CH_INITIATIVES_RANGE_2 = '2'
    CH_INITIATIVES_RANGE_3 = '3'
    CH_INITIATIVES_RANGE_DEFAULT = CH_INITIATIVES_RANGE_1

    CH_INITIATIVES_RANGE = (
        (CH_INITIATIVES_RANGE_1, '0-10'),
        (CH_INITIATIVES_RANGE_2, '10-20'),
        (CH_INITIATIVES_RANGE_3, '20+'),
    )
