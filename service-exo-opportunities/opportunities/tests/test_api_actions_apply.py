from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityApplyAPITest(
        UserTestMixin,
        OpportunityTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_apply_opportunity_with_no_questions(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(questions=0)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        url = reverse(
            'api:opportunity-apply',
            kwargs={'pk': opp.pk})

        # DO ACTION
        response = self.client.post(
            url,
            data={
                'comment': faker.text(),
                'budget': faker.text(),
            })

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    @requests_mock.Mocker()
    def test_apply_opportunity_with_questions_should_validate_all_answered(self, mock_request):

        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(questions=3)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        url = reverse(
            'api:opportunity-apply',
            kwargs={'pk': opp.pk})

        test_cases = [
            {
                'questions_answered': [],
                'status': status.HTTP_400_BAD_REQUEST
            },
            {
                'questions_answered': [
                    {
                        'response': str(faker.boolean()),
                        'question': question.pk,
                    }
                    for question in opp.questions.all()[0:1]
                ],
                'status': status.HTTP_400_BAD_REQUEST
            },
            {
                'questions_answered': [
                    {
                        'response': str(faker.boolean()),
                        'question': question.pk,
                    }
                    for question in opp.questions.all()
                ],
                'status': status.HTTP_200_OK
            },
        ]

        for test_case in test_cases:
            # DO ACTION
            answers = test_case.get('questions_answered')
            expected_response_status = test_case.get('status')
            response = self.client.post(
                url,
                data={
                    'comment': faker.text(),
                    'questions_extra_info': faker.text(),
                    'budget': faker.text(),
                    'answers': answers,
                })

            # ASSERTS
            self.assertEqual(response.status_code, expected_response_status)

    @requests_mock.Mocker()
    def test_apply_opportunity_with_questions(self, mock_request):

        # PREPARE DATA
        self.init_mock(mock_request)
        NUM_QUESTIONS = 3
        opp = self.create_opportunity(questions=NUM_QUESTIONS)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        url = reverse(
            'api:opportunity-apply',
            kwargs={'pk': opp.pk})

        answers_responses = [
            {
                'response': str(faker.boolean()).lower(),
                'question': question.pk,
            }
            for question in opp.questions.all()
        ]

        # DO ACTION
        response = self.client.post(
            url,
            data={
                'comment': faker.text(),
                'questions_extra_info': faker.text(),
                'budget': faker.text(),
                'answers': answers_responses,
            }
        )

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    @requests_mock.Mocker()
    def test_owner_cannot_apply_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        request_mock_account._requests[str(opp.created_by.uuid)]['consultant_id'] = 1
        self.setup_credentials(opp.created_by)
        url = reverse(
            'api:opportunity-apply',
            kwargs={'pk': opp.pk})

        # DO ACTION
        response = self.client.post(
            url,
            data={
                'comment': faker.text(),
                'budget': faker.text(),
            })

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))
