from django.test import TestCase
from django.conf import settings

import requests_mock
import re
from unittest import mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from utils.mock_mixins import MagicMockMixin

from .test_mixin import OpportunityTestMixin, request_mock_account
from ..models import Applicant
from ..tasks import CreateOportunityConversationTask, AddMessageToConversationTask
from ..signals_define import send_message_to_conversation


class ConversationServiceTest(
        UserTestMixin,
        OpportunityTestMixin,
        MagicMockMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_new_conversation_when_apply(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(questions=0)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = Applicant.objects.create_open_applicant(
            user_from=user,
            user=user,
            opportunity=opp,
            summary=faker.text(),
            budget=faker.text())
        matcher = re.compile(
            '{}/conversations/api/{}/conversations/create-group/'.format(
                settings.EXOLEVER_HOST,
                opp.uuid.__str__()))
        mock_request.register_uri(
            'POST',
            matcher,
            json={})

        # DO ACTION
        data = {
            'opportunity_id': opp.id,
            'user_from_id': applicant.user.id,
            'message': '',
            'files': [],
        }
        task = CreateOportunityConversationTask().s(**data).apply()

        # ASSERTS
        self.assertEqual(task.status, 'SUCCESS')

    @requests_mock.Mocker()
    def test_conversation_add_message(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(questions=0)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = Applicant.objects.create_open_applicant(
            user_from=user,
            user=user,
            opportunity=opp,
            summary=faker.text(),
            budget=faker.text())
        matcher = re.compile(
            '{}/conversations/api/{}/conversations/create-message/'.format(
                settings.EXOLEVER_HOST,
                opp.uuid.__str__()))

        mock = mock_request.register_uri(
            'POST',
            matcher,
            json={})

        # DO ACTION
        data = {
            'app_pk': applicant.id,
            'user_from': applicant.user.uuid.__str__(),
            'message': faker.text(),
        }
        task = AddMessageToConversationTask().s(**data).apply()

        # ASSERTS
        self.assertEqual(task.status, 'SUCCESS')
        self.assertTrue(mock.called)
        request_data = mock.last_request.json()
        self.assertEqual(
            request_data['conversation_created_by'],
            user.uuid.__str__())
        self.assertEqual(
            request_data['created_by'],
            user.uuid.__str__())
        self.assertEqual(
            request_data['message'],
            data['message'])

    @requests_mock.Mocker()
    def test_add_message_when_assign(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(questions=0)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = Applicant.objects.create_open_applicant(
            user_from=user,
            user=user,
            opportunity=opp,
            summary=faker.text(),
            budget=faker.text())
        response_message = faker.text()
        data = self.get_sow_data()
        handler = mock.Mock()
        send_message_to_conversation.connect(
            handler, sender=applicant.__class__)

        # DO ACTION
        opp.assign(self.super_user, applicant, response_message, **data)

        # ASSERTS
        self.assertTrue(handler.called)
        self.assertEqual(
            self.get_mock_kwarg(handler, 'user_from'),
            self.super_user)
        self.assertEqual(
            self.get_mock_kwarg(handler, 'message'),
            response_message)
        self.assertEqual(
            self.get_mock_kwarg(handler, 'applicant'),
            applicant)
