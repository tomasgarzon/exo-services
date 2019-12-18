from django.test import TestCase
import requests_mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .test_mixin import OpportunityTestMixin, request_mock_account
from ..models import Applicant


class OpportunityApplyAPITest(
        UserTestMixin,
        OpportunityTestMixin,
        TestCase):

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

        # DO ACTION
        Applicant.objects.create_open_applicant(
            user_from=user,
            user=user,
            opportunity=opp,
            summary=faker.text(),
            budget=faker.text())

        # ASSERTS
        opp.refresh_from_db()
        self.assertTrue(opp.is_requested)
        self.assertEqual(opp.applicants_info.count(), 1)
        self.assertIsNotNone(opp.applicants_info.first().budget)
        self.assertIsNotNone(opp.applicants_info.first().summary)
        self.assertFalse(opp.questions.exists())

    @requests_mock.Mocker()
    def test_apply_opportunity_with_questions(self, mock_request):

        # PREPARE DATA
        self.init_mock(mock_request)
        NUM_QUESTIONS = 3
        opp = self.create_opportunity(questions=NUM_QUESTIONS)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)

        answers_responses = [
            {
                'response': str(faker.boolean()).lower(),
                'question': question,
            }
            for question in opp.questions.all()
        ]

        # DO ACTION
        Applicant.objects.create_open_applicant(
            user_from=user,
            user=user,
            opportunity=opp,
            summary=faker.text(),
            budget=faker.text(),
            questions_extra_info=faker.word(),
            answers=answers_responses)

        # ASSERTS
        opp.refresh_from_db()
        self.assertTrue(opp.is_requested)
        self.assertEqual(opp.applicants_info.count(), 1)
        self.assertIsNotNone(opp.applicants_info.first().budget)
        self.assertIsNotNone(opp.applicants_info.first().summary)
        self.assertIsNotNone(opp.applicants_info.first().questions_extra_info)
        self.assertEqual(opp.applicants_info.first().answers.count(), NUM_QUESTIONS)
