from django.test import TestCase
from django.utils import timezone
from django.core import management
from django.utils.six import StringIO

from datetime import timedelta
import requests_mock

from utils.test_mixin import UserTestMixin

from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityCommandDeadlineTest(
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
    def test_close_opportunities_by_command(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        # Opp requested with deadline for today
        opp = self.create_opportunity()
        opp.deadline_date = timezone.now().date()
        opp.save()

        # Opp requested with deadline for tomorrow
        opp2 = self.create_opportunity()
        opp2.deadline_date = timezone.now().date() + timedelta(days=1)
        opp2.save()

        # Opp closed with deadline for today
        opp3 = self.create_opportunity()
        opp3.deadline_date = timezone.now().date()
        opp3.save()
        opp3.close(opp.created_by)

        opportunities = [opp, opp2, opp3]
        out = StringIO()
        err = StringIO()

        # ACTION
        management.call_command(
            'opportunity_deadline', stdout=out, stderr=err)

        # ASSERTS
        for opp in opportunities:
            opp.refresh_from_db()
        self.assertTrue(opportunities[0].is_closed)
        self.assertFalse(opportunities[1].is_closed)
        self.assertTrue(opportunities[2].is_closed)

    @requests_mock.Mocker()
    def test_reminder_opportunities_by_command(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        opp = self.create_opportunity()
        opp.deadline_date = timezone.now().date() + timedelta(days=1)
        opp.save()

        opp2 = self.create_opportunity()
        opp2.deadline_date = timezone.now().date() + timedelta(days=3)
        opp2.save()

        out = StringIO()
        err = StringIO()

        # ACTION
        management.call_command(
            'opportunity_deadline', stdout=out, stderr=err)

        # ASSERTS
        out.seek(0)

        # first line is information command
        out.readline()
        data = eval(out.readline())
        self.assertEqual(
            data['title'], '{}'.format(opp2.title))
        data = eval(out.readline())
        self.assertEqual(
            data['title'], '{}'.format(opp.title))
