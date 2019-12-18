from django.test import TestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .test_mixin import OpportunityTestMixin
from ..management.commands.opportunity_report_finance import Command
from ..models import Applicant


class OpportunityCommandFinanceReportTest(
        UserTestMixin,
        OpportunityTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()

    def get_feedback(self):
        return {
            'comment': faker.text(),
            'explained': 1,
            'collaboration': 2,
            'communication': 3,
            'recommendation': 4,
        }

    def test_filtering_applicants_for_report(self):
        # PREPARE DATA
        opp = self.create_opportunity()
        applicants_expected = []
        user_creator = opp.created_by

        # applicant feedback pending
        user = self.get_user()
        applicant = Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(self.super_user, applicant)
        applicant.set_completed()

        # applicant give feedback, requester not
        user = self.get_user()
        applicant = Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(user_creator, applicant)
        applicant.set_completed()
        applicant.give_feedback(user, **self.get_feedback())

        # applicant give feedback, requester not and expired feedback
        user = self.get_user()
        applicant = Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(user_creator, applicant)
        applicant.set_completed()
        applicant.give_feedback(user, **self.get_feedback())
        applicant.set_feedback_expired()
        applicants_expected.append(applicant)

        # requester give feedback, applicant not
        user = self.get_user()
        applicant = Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(user_creator, applicant)
        applicant.set_completed()
        applicant.give_feedback(opp.created_by, **self.get_feedback())
        applicants_expected.append(applicant)

        # not requester neither applicant give feedback
        user = self.get_user()
        applicant = Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(user_creator, applicant)
        applicant.set_completed()
        applicant.set_feedback_expired()
        applicants_expected.append(applicant)

        command = Command()

        # DO ACTION
        applicants = command.get_applicants_feedback_received()

        # DO ASSERTS
        self.assertEqual(
            set(applicants),
            set(applicants_expected))
