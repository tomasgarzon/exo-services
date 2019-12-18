from django.conf import settings
from django.test import TestCase

import re
import requests_mock
from unittest.mock import patch
from unittest import mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from utils.mock_mixins import MagicMockMixin

from .. import models
from ..tasks import (
    NewOpportunityTask,
    NewApplicantTask,
    OpportunitySelectedTask,
    OpportunityNotSelectedTask,
    OpportunityRemovedTask,
    OpportunityEditedTask,
    OpportunityMessageReceivedTask
)
from ..signals_define import opportunity_post_edited
from ..signals.helpers import send_email_when_opportunity_is_closed
from ..tasks.conversation_message import MAIL_CHAT_FIRST_MESSAGE
from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityEmailDataTest(
        UserTestMixin,
        MagicMockMixin,
        OpportunityTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()

        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

        self.opportunity_creator = self.get_user()
        request_mock_account.add_mock(
            self.opportunity_creator, is_consultant=True, is_superuser=False)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_notification_for_new_opportunity(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        matcher = re.compile(
            '{}/api/accounts/user/can-receive-opportunities/'.format(
                settings.EXOLEVER_HOST))
        mock_response = []
        NUM_CONSULTANTS = 3
        for _ in range(NUM_CONSULTANTS):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            mock_response.append({
                'email': faker.email(),
                'uuid': str(user.uuid)})
        mock_request.register_uri(
            'GET',
            matcher,
            json=mock_response)
        opp = self.create_opportunity()

        # DO ACTION
        with self.settings(OPPORTUNITIES_SEND_WHEN_CREATED=True):
            task = NewOpportunityTask().s(pk=opp.pk).apply()

            # ASSERTS
            self.assertEqual(task.status, 'SUCCESS')
            self.assertTrue(mock_email.called)
            self.assertEqual(mock_email.call_count, NUM_CONSULTANTS)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_notification_for_new_tagged_opportunity(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        matcher = re.compile(
            '{}/api/accounts/user/can-receive-opportunities/'.format(
                settings.EXOLEVER_HOST))
        mock_response = []
        NUM_CONSULTANTS = 3
        for _ in range(NUM_CONSULTANTS):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            mock_response.append({
                'email': faker.email(),
                'uuid': str(user.uuid)})
        mock_request.register_uri(
            'GET',
            matcher,
            json=mock_response)
        opp = self.create_opportunity(target=settings.OPPORTUNITIES_CH_TARGET_FIXED)
        # OPP TAGGED TO ONLY ONE USER
        opp.users_tagged.create(user=user)

        # DO ACTION
        task = NewOpportunityTask().s(pk=opp.pk).apply()

        # ASSERTS
        self.assertEqual(task.status, 'SUCCESS')
        self.assertTrue(mock_email.called)
        self.assertEqual(mock_email.call_count, 1)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_notification_for_new_applicant(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(self.opportunity_creator)

        user_applicant = self.get_user()
        request_mock_account.add_mock(
            user_applicant, is_consultant=True, is_superuser=False)
        opportunity_applicant = models.Applicant.objects.create_open_applicant(
            user_from=user_applicant,
            user=user_applicant,
            opportunity=opp,
            summary=faker.text(),
        )

        # DO ACTION
        task = NewApplicantTask().s(
            pk=opp.pk,
            applicant_pk=opportunity_applicant.pk,
        ).apply()

        # ASSERTS
        opportunity_creator_email = request_mock_account.get_request(
            str(self.opportunity_creator.uuid)
        ).get('email')
        self.assertEqual(task.status, 'SUCCESS')
        self.assertTrue(mock_email.called)
        recipients = self.get_mock_kwarg(mock_email, 'recipients')
        self.assertEqual(recipients, [opportunity_creator_email])

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_for_select_applicant(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        applicant_user = self.get_user()
        request_mock_account.add_mock(
            applicant_user, is_consultant=True, is_superuser=False)

        opp = self.create_opportunity()
        applicant = models.Applicant.objects.create_open_applicant(
            user_from=applicant_user,
            user=applicant_user,
            opportunity=opp,
            summary=faker.text()
        )
        sow_data = self.get_sow_data()
        opp.assign(self.super_user, applicant, **sow_data)

        # DO ACTION
        task = OpportunitySelectedTask().s(
            pk=opp.pk,
            applicant_pk=applicant.pk).apply()

        # ASSERTS
        applicant_email = request_mock_account.get_request(
            str(applicant_user.uuid)
        ).get('email')
        self.assertEqual(task.status, 'SUCCESS')
        self.assertTrue(mock_email.called)
        self.assertEqual(mock_email.call_count, 1)
        recipients = self.get_mock_kwarg(mock_email, 'recipients')
        self.assertEqual(recipients, [applicant_email])

        # ASSERTS ATTACHMENTS
        attachments = self.get_mock_kwarg(mock_email, 'attachments')
        self.assertTrue(len(attachments))
        attach_file = attachments[0]
        self.assertEqual(
            attach_file.get_filename(),
            'invite.ics',
        )
        self.assertEqual(
            attach_file.get_content_type(),
            'text/calendar',
        )
        self.assertEqual(
            opp.category.code,
            self.get_mock_kwarg(mock_email, 'category_code')
        )

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_for_reject_applicant(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        applicant_user = self.get_user()
        request_mock_account.add_mock(
            applicant_user, is_consultant=True, is_superuser=False)

        opp = self.create_opportunity()
        applicant = models.Applicant.objects.create_open_applicant(
            user_from=applicant_user,
            user=applicant_user,
            opportunity=opp,
            summary=faker.text()
        )
        opp.assign(self.super_user, applicant)

        # DO ACTION
        task = OpportunityNotSelectedTask().s(
            pk=opp.pk,
            user_pk=applicant_user.pk).apply()

        # ASSERTS
        applicant_email = request_mock_account.get_request(
            str(applicant_user.uuid)
        ).get('email')
        self.assertEqual(task.status, 'SUCCESS')
        self.assertTrue(mock_email.called)
        self.assertEqual(mock_email.call_count, 1)
        recipients = self.get_mock_kwarg(mock_email, 'recipients')
        self.assertEqual(recipients, [applicant_email])

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_when_remove_opportunity(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        applicant_user = self.get_user()
        request_mock_account.add_mock(
            applicant_user, is_consultant=True, is_superuser=False)

        opp = self.create_opportunity()
        models.Applicant.objects.create_open_applicant(
            user_from=applicant_user,
            user=applicant_user,
            opportunity=opp,
            summary=faker.text()
        )
        comment = faker.text()

        # DO ACTION
        task = OpportunityRemovedTask().s(
            pk=opp.pk,
            comment=comment).apply()

        # ASSERTS
        applicant_email = request_mock_account.get_request(
            str(applicant_user.uuid)
        ).get('email')
        self.assertEqual(task.status, 'SUCCESS')
        self.assertTrue(mock_email.called)
        self.assertEqual(mock_email.call_count, 1)
        recipients = self.get_mock_kwarg(mock_email, 'recipients')
        self.assertEqual(
            self.get_mock_kwarg(mock_email, 'comment'),
            comment)
        self.assertEqual(recipients, [applicant_email])

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_when_remove_opportunity_with_several_applicants(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        applicant_user = self.get_user()
        request_mock_account.add_mock(
            applicant_user, is_consultant=True, is_superuser=False)

        extra_applicant_user = self.get_user()
        request_mock_account.add_mock(
            extra_applicant_user, is_consultant=True, is_superuser=False)

        opp = self.create_opportunity()
        models.Applicant.objects.create_open_applicant(
            user_from=applicant_user,
            user=applicant_user,
            opportunity=opp,
            summary=faker.text()
        )
        models.Applicant.objects.create_open_applicant(
            user_from=extra_applicant_user,
            user=extra_applicant_user,
            opportunity=opp,
            summary=faker.text()
        )
        comment = faker.text()

        # DO ACTION
        task = OpportunityRemovedTask().s(
            pk=opp.pk,
            comment=comment).apply()

        # ASSERTS
        self.assertEqual(task.status, 'SUCCESS')
        self.assertTrue(mock_email.called)
        self.assertEqual(mock_email.call_count, 2)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_when_edit_opportunity(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        applicant_user = self.get_user()
        request_mock_account.add_mock(
            applicant_user, is_consultant=True, is_superuser=False)
        models.Applicant.objects.create_open_applicant(
            user_from=applicant_user,
            user=applicant_user,
            opportunity=opp,
            summary=faker.text()
        )

        # DO ACTION
        task = OpportunityEditedTask().s(
            pk=opp.pk,
            comment=faker.text()).apply()

        # ASSERTS
        applicant_user_email = request_mock_account.get_request(
            str(applicant_user.uuid)
        ).get('email')
        self.assertEqual(task.status, 'SUCCESS')
        self.assertTrue(mock_email.called)
        self.assertEqual(mock_email.call_count, 1)
        recipients = self.get_mock_kwarg(mock_email, 'recipients')
        self.assertEqual(recipients, [applicant_user_email])

    @requests_mock.Mocker()
    def test_notification_signal_for_editing(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.handler = mock.Mock()
        opportunity_post_edited.connect(self.handler)
        opp = self.create_opportunity()
        comment = faker.text()

        # DO ACTION
        models.Opportunity.objects.update_opportunity(
            user_from=opp.created_by,
            opportunity=opp,
            keywords=[],
            questions=[],
            comment=comment,
            target=opp.target,
            users_tagged=[],
            send_notification=True)

        # ASSERTS
        self.assertEqual(
            self.get_mock_kwarg(self.handler, 'comment'),
            comment)
        self.assertEqual(self.handler.call_count, 1)
        opportunity_post_edited.disconnect(self.handler)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_when_close_manually_opportunity(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        opp = self.create_opportunity()
        models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        comment = faker.text()
        applicant_list = opp.applicants_info.pending_applicants().users()

        # DO ACTION
        send_email_when_opportunity_is_closed(
            opp, applicant_list,
            settings.OPPORTUNITIES_CH_CLOSE_MANUALLY,
            comment=comment)

        # ASSERTS
        self.assertEqual(mock_email.call_count, 1)
        self.assertEqual(
            self.get_mock_kwarg(mock_email, 'comment'),
            comment)
        self.assertEqual(
            self.get_mock_kwarg(mock_email, 'template'),
            settings.OPPORTUNITIES_MAIL_VIEW_CLOSED_MANUALLY)
        self.assertEqual(
            self.get_mock_kwarg(mock_email, 'recipients'),
            [request_mock_account.get_request(user.uuid.__str__())['email']])

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_when_close_deadline_opportunity(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        opp = self.create_opportunity()
        models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        user_list = opp.applicants_info.pending_applicants().users()

        # DO ACTION
        send_email_when_opportunity_is_closed(
            opp, user_list,
            settings.OPPORTUNITIES_CH_CLOSE_DEADLINE)

        # ASSERTS
        mock_kwargs_requester = None
        mock_kwargs_applicant = None
        self.assertEqual(mock_email.call_count, 2)
        for _, mock_kwargs in mock_email.call_args_list:
            self.assertIsNone(mock_kwargs.get('comment'))
            if mock_kwargs.get('template').endswith('requester'):
                mock_kwargs_requester = mock_kwargs
            elif mock_kwargs.get('template') == settings.OPPORTUNITIES_MAIL_VIEW_CLOSED_MANUALLY:
                mock_kwargs_applicant = mock_kwargs

        self.assertIsNotNone(mock_kwargs_requester)
        self.assertIsNotNone(mock_kwargs_applicant)
        self.assertEqual(
            mock_kwargs_requester.get('recipients'),
            [request_mock_account.get_request(opp.created_by.uuid.__str__())['email']])
        self.assertEqual(
            mock_kwargs_applicant.get('recipients'),
            [request_mock_account.get_request(user.uuid.__str__())['email']])

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_when_close_positions_covered_opportunity(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        opp = self.create_opportunity()
        models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        user_list = opp.applicants_info.pending_applicants().users()

        # DO ACTION
        send_email_when_opportunity_is_closed(
            opp, user_list,
            settings.OPPORTUNITIES_CH_CLOSE_POSITIONS)

        # ASSERTS
        mock_kwargs_requester = None
        mock_kwargs_applicant = None
        self.assertEqual(mock_email.call_count, 2)
        for _, mock_kwargs in mock_email.call_args_list:
            self.assertIsNone(mock_kwargs.get('comment'))
            if mock_kwargs.get('template') == settings.OPPORTUNITIES_MAIL_VIEW_CLOSED_BY_POSITIONS:
                mock_kwargs_requester = mock_kwargs
            elif mock_kwargs.get('template') == settings.OPPORTUNITIES_MAIL_VIEW_APPLICANT_NOT_SELECTED:
                mock_kwargs_applicant = mock_kwargs

        self.assertIsNotNone(mock_kwargs_requester)
        self.assertIsNotNone(mock_kwargs_applicant)
        self.assertEqual(
            mock_kwargs_requester.get('recipients'),
            [request_mock_account.get_request(opp.created_by.uuid.__str__())['email']])
        self.assertEqual(
            mock_kwargs_applicant.get('recipients'),
            [request_mock_account.get_request(user.uuid.__str__())['email']])

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_when_applicant_write_first_message(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        opp = self.create_opportunity()
        mock_request.register_uri(
            'GET',
            re.compile(
                '{}/api/account-config/config_param/{}/'.format(
                    settings.EXOLEVER_HOST,
                    opp.created_by.uuid.__str__())),
            json=[{'name': 'new_conversation', 'value': True}])

        # DO ACTION
        OpportunityMessageReceivedTask().s(
            pk=opp.pk,
            message=faker.text(),
            created_by=user.uuid,
            other_user=opp.created_by.uuid,
        ).apply()

        # ASSERTS
        self.assertEqual(mock_email.call_count, 1)
        _, mock_kwargs = mock_email.call_args_list[0]
        self.assertIsNotNone(mock_kwargs.get('public_url'))
        self.assertIsNotNone(mock_kwargs.get('title'))
        self.assertIsNotNone(mock_kwargs.get('user_from_full_name'))
        self.assertIsNotNone(mock_kwargs.get('message'))
        self.assertEqual(
            request_mock_account.get_request(user.uuid.__str__())['fullName'],
            mock_kwargs.get('user_from_full_name')
        )
        self.assertEqual(
            mock_kwargs.get('template'),
            MAIL_CHAT_FIRST_MESSAGE)
        self.assertEqual(
            mock_kwargs.get('recipients'),
            [request_mock_account.get_request(opp.created_by.uuid.__str__())['email']])

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_when_requester_write_first_message(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        opp = self.create_opportunity()
        mock_request.register_uri(
            'GET',
            re.compile(
                '{}/api/account-config/config_param/{}/'.format(
                    settings.EXOLEVER_HOST,
                    user.uuid.__str__())),
            json=[{'name': 'new_conversation', 'value': True}])
        # DO ACTION
        OpportunityMessageReceivedTask().s(
            pk=opp.pk,
            message=faker.text(),
            created_by=opp.created_by.uuid,
            other_user=user.uuid,
        ).apply()

        # ASSERTS
        self.assertEqual(mock_email.call_count, 1)
        _, mock_kwargs = mock_email.call_args_list[0]
        self.assertIsNotNone(mock_kwargs.get('public_url'))
        self.assertIsNotNone(mock_kwargs.get('title'))
        self.assertIsNotNone(mock_kwargs.get('user_from_full_name'))
        self.assertIsNotNone(mock_kwargs.get('message'))
        self.assertEqual(
            mock_kwargs.get('template'),
            MAIL_CHAT_FIRST_MESSAGE)
        self.assertEqual(
            request_mock_account.get_request(opp.created_by.uuid.__str__())['fullName'],
            mock_kwargs.get('user_from_full_name')
        )
        self.assertEqual(
            mock_kwargs.get('recipients'),
            [request_mock_account.get_request(user.uuid.__str__())['email']])

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_email_created_not_receive_notification_new_opportunity(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        matcher = re.compile(
            '{}/api/accounts/user/can-receive-opportunities/'.format(
                settings.EXOLEVER_HOST))
        mock_response = []
        NUM_CONSULTANTS = 3
        for _ in range(NUM_CONSULTANTS):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            mock_response.append({
                'email': faker.email(),
                'uuid': str(user.uuid)})
        last_user = user
        mock_request.register_uri(
            'GET',
            matcher,
            json=mock_response)
        opp = self.create_opportunity(user=last_user)

        # DO ACTION send True
        with self.settings(OPPORTUNITIES_SEND_WHEN_CREATED=True):
            task = NewOpportunityTask().s(pk=opp.pk).apply()
            # ASSERTS
            self.assertEqual(task.status, 'SUCCESS')
            self.assertTrue(mock_email.called)
            self.assertEqual(mock_email.call_count, NUM_CONSULTANTS - 1)

        # DO ACTION send False
        task = NewOpportunityTask().s(pk=opp.pk).apply()
        # ASSERTS
        mock_email.reset_mock()
        self.assertEqual(task.status, 'SUCCESS')
        self.assertFalse(mock_email.called)
