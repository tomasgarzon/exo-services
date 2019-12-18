from django.test import TestCase

import requests_mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from utils.mock_mixins import MagicMockMixin

from .. import models
from .test_mixin import OpportunityTestMixin, request_mock_account
from ..mails import (
    Create, NewApplicant, ApplicantNotSelected, ApplicantSelected,
    Edit, Remove, OpportunityClosed, OpportunityCloseReminder)


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

    @requests_mock.Mocker()
    def test_data_for_new_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()

        # DO ACTIONS
        data = Create(opp).get_data()

        # ASSERTS
        self.assertIsNotNone(data)
        email_fields = [
            'description',
            'title',
            'created_by_profile_picture',
            'created_by_name',
            'created_by_role',
            'entity_name',
            'location_string',
            'start_date',
            'duration',
            'tags',
            'budget_string',
            'public_url',
            'num_positions',
        ]
        for field in email_fields:
            self.assertIsNotNone(data.get(field), '{} not found'.format(field))

    @requests_mock.Mocker()
    def test_data_for_new_applicant(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        answers = [
            {'question': question, 'response': 'True'}
            for question in opp.questions.all()
        ]
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text(),
            answers=answers)

        # DO ACTIONS
        data = NewApplicant(applicant).get_data()

        # ASSERTS
        self.assertIsNotNone(data)
        email_fields = [
            'title',
            'applicant_name',
            'applicant_profile_picture',
            'applicant_role',
            'summary',
            'questions_extra_info',
            'applicant_email',
            'applicant_profile_url',
            'public_url',
            'answers',
        ]
        for field in email_fields:
            self.assertTrue(field in data.keys())

    @requests_mock.Mocker()
    def test_data_applicant_not_selected(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())

        # DO ACTIONS
        data = ApplicantNotSelected(opp, user).get_data()

        # ASSERTS
        self.assertIsNotNone(data)
        email_fields = [
            'title',
            'applicant_name',
            'created_by_name',
            'public_url',
        ]
        for field in email_fields:
            self.assertIsNotNone(data.get(field), '{} not found'.format(field))

    @requests_mock.Mocker()
    def test_data_applicant_selected(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())

        # DO ACTIONS
        data = ApplicantSelected(applicant).get_data()

        # ASSERTS
        self.assertIsNotNone(data)
        email_fields = [
            'title',
            'applicant_name',
            'created_by_name',
            'public_url',
            'opportunity_url',
        ]
        for field in email_fields:
            self.assertIsNotNone(data.get(field), '{} not found'.format(field))

    @requests_mock.Mocker()
    def test_data_remove(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        opp.remove(self.super_user)

        # DO ACTIONS
        data = Remove(opp).get_data()

        # ASSERTS
        self.assertIsNotNone(data)
        email_fields = [
            'title',
            'created_by_name',
            'public_url',
        ]
        for field in email_fields:
            self.assertIsNotNone(data.get(field), '{} not found'.format(field))

    @requests_mock.Mocker()
    def test_data_edit(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()

        # DO ACTIONS
        data = Edit(opp).get_data()

        # ASSERTS
        self.assertIsNotNone(data)
        email_fields = [
            'title',
            'created_by_name',
            'public_url',
        ]
        for field in email_fields:
            self.assertIsNotNone(data.get(field), '{} not found'.format(field))

    @requests_mock.Mocker()
    def test_data_close(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()

        # DO ACTIONS
        data = OpportunityClosed(opp).get_data()

        # ASSERTS
        self.assertIsNotNone(data)
        email_fields = [
            'title',
            'created_by_name',
            'public_url',
        ]
        for field in email_fields:
            self.assertIsNotNone(data.get(field), '{} not found'.format(field))

    @requests_mock.Mocker()
    def test_data_reminder_before_closing(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()

        # DO ACTIONS
        data = OpportunityCloseReminder(opp).get_data()

        # ASSERTS
        self.assertIsNotNone(data)
        email_fields = [
            'title',
            'created_by_name',
            'duedate',
            'public_url',
        ]
        for field in email_fields:
            self.assertIsNotNone(data.get(field), '{} not found'.format(field))
