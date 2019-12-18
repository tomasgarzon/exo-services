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


class FrontendConfig(AppConf):

    FEEDBACK_TO = ['support@openexo.com']
    DEMO_GROUP_NAME = 'test-demo'
    DELIVERY_MANAGER_GROUP = 'delivery-manager'

    CIRCLES_PAGE = '/ecosystem/circles'
    CIRCLE_DETAIL_PAGE = '/ecosystem/circles/{slug}'
    POST_DETAIL_PAGE = '/ecosystem/circles/{circle}/{slug}'
    JOBS_SWARM_SESSION_QUESTION_PAGE = '/ecosystem/jobs/swarm-session/{pk_qa_session}/{pk}/'
    JOBS_SWARM_PAGE = '/ecosystem/jobs/swarm-session/{pk}'
    PROJECT_QUESTION_PAGE = '/platform/service/{project_id}/team/{team_id}/{section}/{pk}'
    DIRECTORY_PAGE = '/ecosystem/directory'
    OPPORTUNITIES_PAGE = '/ecosystem/opportunities'
    MY_JOBS_PAGE = '/ecosystem/jobs'
    USER_ACCOUNTS_PAGE = '/ecosystem/profile/accounts/{pk}'
    USER_PROFILE_EDIT_PAGE = '/ecosystem/profile/{pk}/edit/{section}'
    USER_PROFILE_PAGE = '/ecosystem/profile/{pk}'
    USER_PROFILE_DIRECTORY_PAGE = '/ecosystem/{section}/profile/{pk}'
    USER_PROFILE_PUBLIC_PAGE = '/public/profile/{slug}'
    PROJECT_STEP_PAGE = '/platform/service/{project_id}/team/{team_id}/step/{step_id}/{section}'
    PROJECT_PAGE = '/platform/service/{project_id}/team/{team_id}/{section}'
    PROJECT_PROFILE_PAGE = '/ecosystem/projects/profile/{slug}/{section}'
    ADVISORY_CALL_DETAIL_PAGE = '/ecosystem/opportunities/advisory-call/{pk}'
    INVITATION_PAGE = '/invitations/pending/{hash}'
    AUTH_SIGNUP_PAGE = '/auth/signup/{hash}'
    REGISTRATION_STEP_PAGE = '/signup/{section}/{hash}'
    PASSWORD_RESET_PAGE = '/password/reset/{token}/{cipher_email}'
    MESSAGES_PAGE = '/ecosystem/mailbox/list'
