from django.test import TestCase
from django.utils import timezone
from django.core import management
from django.utils.six import StringIO
from django.conf import settings

from datetime import timedelta
import requests_mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .. import models
from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityCommandFeedbackTest(
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
    def test_feedback_applicant_by_command(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        # Opp requested with deadline for today
        opp = self.create_opportunity()

        # SELECTED end_date for today
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app_first = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        sow_data = self.get_sow_data()
        sow_data['end_date'] = timezone.now().date()
        opp.assign(self.super_user, app_first, faker.text(), **sow_data)

        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        sow_data = self.get_sow_data()
        opp.assign(self.super_user, app, faker.text(), **sow_data)

        out = StringIO()
        err = StringIO()

        # ACTION
        management.call_command(
            'opportunity_feedback', stdout=out, stderr=err)

        print(err)

        # ASSERTS
        out.seek(0)

        applicant_pk = out.readline().replace('\n', '')
        self.assertEqual(
            applicant_pk, 'Completed: {}'.format(app_first.pk.__str__()))
        app.refresh_from_db()
        self.assertFalse(app.is_completed)
        app_first.refresh_from_db()
        self.assertTrue(app_first.is_completed)

    @requests_mock.Mocker()
    def test_feedback_both_reminder_by_command(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        # Opp requested with deadline for today
        opp = self.create_opportunity()

        # SELECTED end_date 2 days ago
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        sow_data = self.get_sow_data()
        sow_data['end_date'] = (timezone.now() - timedelta(days=2)).date()
        opp.assign(self.super_user, app, faker.text(), **sow_data)
        app.set_completed()
        out = StringIO()
        err = StringIO()

        # ACTION
        management.call_command(
            'opportunity_feedback', stdout=out, stderr=err)

        # ASSERTS
        out.seek(0)

        applicant_pk = out.readline().replace('\n', '')
        self.assertEqual(
            applicant_pk, 'Requester reminder: {}'.format(app.pk))

        applicant_pk = out.readline().replace('\n', '')
        self.assertEqual(
            applicant_pk, 'Applicant reminder: {}'.format(app.pk))

    @requests_mock.Mocker()
    def test_feedback_given(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        # Opp requested with deadline for today
        opp = self.create_opportunity()

        # SELECTED end_date 2 days ago
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        sow_data = self.get_sow_data()
        sow_data['end_date'] = (timezone.now() - timedelta(days=2)).date()
        opp.assign(self.super_user, app, faker.text(), **sow_data)
        app.set_status = None, settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_READY
        out = StringIO()
        err = StringIO()

        # ACTION
        management.call_command(
            'opportunity_feedback', stdout=out, stderr=err)

        # ASSERTS
        out.seek(0)
        self.assertEqual(out.readline(), '')

    @requests_mock.Mocker()
    def test_feedback_expired_by_command(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        # Opp requested with deadline for today
        opp = self.create_opportunity()

        # SELECTED end_date 7 days ago
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        sow_data = self.get_sow_data()
        sow_data['end_date'] = (timezone.now() - timedelta(days=7)).date()
        opp.assign(self.super_user, app, faker.text(), **sow_data)
        app.set_completed()
        out = StringIO()
        err = StringIO()

        # ACTION
        management.call_command(
            'opportunity_feedback', stdout=out, stderr=err)

        # ASSERTS
        out.seek(0)

        applicant_pk = out.readline().replace('\n', '')
        self.assertEqual(
            applicant_pk, 'Requester expired: {}'.format(app.pk))

        applicant_pk = out.readline().replace('\n', '')
        self.assertEqual(
            applicant_pk, 'Applicant expired: {}'.format(app.pk))

        app.refresh_from_db()
        self.assertTrue(app.is_feedback_received)
