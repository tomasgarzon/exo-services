import uuid

from django.urls import reverse
from django.conf import settings

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.mock_mixins import MagicMockMixin
from utils.faker_factory import faker

from .. import models

from .test_mixin import OpportunityTestMixin, request_mock_account
from ..faker_factories import FakeOpportunityGroupFactory


class User:
    uuid = None


class OpportunityAPITest(
        UserTestMixin,
        OpportunityTestMixin,
        MagicMockMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_migrate_open(self, mock_request):
        # PREPARE DATA

        self.init_mock(mock_request)
        self.setup_username_credentials()
        group = FakeOpportunityGroupFactory.create(
            related_uuid=uuid.uuid4(),
            budgets=[
                {
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_EUR,
                    'budget': '{}.0'.format(int(faker.numerify()))
                },
                {
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_EXOS,
                    'budget': '{}.0'.format(int(faker.numerify()))
                },
            ]
        )
        users = [
            'd5365d93-db73-4156-99b7-c3f9bf8f8b9c',
            '4e2180f0-d452-4585-b105-dded2f2f9143',
            'd89ac859-7698-460a-b5a2-9517bf7c6a4d',
            '8b5b81d0-b8f6-4348-93ff-ea101a3d7066',
            '22cedaaa-f1c9-498e-9302-505beaf64983',
            '2c9551cf-887a-4b9b-9985-aaf858b055e7',
            'c092e91c-dcbe-4545-aa67-2a90128a58d3',
        ]
        for user_uuid in users:
            user = User()
            user.uuid = user_uuid
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)

        example_data = {
            'group': group.id.__str__(),
            'title': 'How to build a trust architecture?',
            'description': 'Our team is looking for someone .',
            'keywords': [{'name': 'Blockchain'}, {'name': 'Ecosystems'}, {'name': 'ExOs'}, {'name': 'Trust'}],
            'deadline_date': '2019-11-08',
            'slug': 'how-to-build-a-trust-architecture',
            'mode': 'L',
            'uuid': '96a8a57e-ed1d-40f7-b4bb-582bd4f06a01',
            'target': 'O',
            'users_tagged': [],
            'applicants': [
                {
                    'user': 'd5365d93-db73-4156-99b7-c3f9bf8f8b9c',
                    'summary': 'Hi There,', 'status': 'J'},
                {
                    'user': '4e2180f0-d452-4585-b105-dded2f2f9143',
                    'summary': 'Trust is based on track record showing'
                    ' ability to consistently deliver.', 'status': 'J'},
                {
                    'user': 'd89ac859-7698-460a-b5a2-9517bf7c6a4d',
                    'summary': 'I have experience in financial services ', 'status': 'J'},
                {
                    'user': '8b5b81d0-b8f6-4348-93ff-ea101a3d7066',
                    'summary': 'As you know my work is largely around enterprise', 'status': 'J'},
                {
                    'user': '22cedaaa-f1c9-498e-9302-505beaf64983',
                    'summary': 'Experienced (and highly rated :) ExO Advisor.',
                    'status': 'H', 'slot': '2019-11-07T20:00:00+00:00'},
                {
                    'user': '2c9551cf-887a-4b9b-9985-aaf858b055e7',
                    'summary': 'One of my main services', 'status': 'J'
                }
            ],
            'created': '2019-11-01T09:04:19.883443+00:00',
            'history': [
                {
                    'created': '2019-11-11T15:41:16.716774+00:00',
                    'status': 'H',
                    'user': 'c092e91c-dcbe-4545-aa67-2a90128a58d3'
                },
                {
                    'created': '2019-11-10T14:09:59.909408+00:00',
                    'status': 'C',
                    'user': 'c092e91c-dcbe-4545-aa67-2a90128a58d3'
                },
                {
                    'created': '2019-11-10T14:09:59.871819+00:00',
                    'status': 'C',
                    'user': 'c092e91c-dcbe-4545-aa67-2a90128a58d3'
                },
                {
                    'created': '2019-11-10T14:09:59.439327+00:00',
                    'status': 'S',
                    'user': 'c092e91c-dcbe-4545-aa67-2a90128a58d3'
                },
                {
                    'created': '2019-11-01T09:05:04.682074+00:00',
                    'status': 'R',
                    'user': 'c092e91c-dcbe-4545-aa67-2a90128a58d3'
                },
                {
                    'created': '2019-11-01T09:04:19.908384+00:00',
                    'status': 'X',
                    'user': 'c092e91c-dcbe-4545-aa67-2a90128a58d3'
                }
            ],
            'status': 'L',
            'ratings': [
                {
                    'user': 'c092e91c-dcbe-4545-aa67-2a90128a58d3',
                    'rating': 2}
            ],
            'files': [{
                'filestack_status': 'Stored',
                'url': 'https://cdn.filestackcontent.com/Lr59QG8oQRWliC6x70cx',
                'filename': 'gato.jpg',
                'mimetype': 'image/jpeg'}]
        }

        url = reverse('api:migrate')

        # DO ACTION
        response = self.client.post(url, data=example_data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opp = models.Opportunity.objects.get(group=group)
        self.assertEqual(opp.uuid.__str__(), example_data.get('uuid'))
        self.assertEqual(opp.group, group)
        self.assertEqual(
            opp.applicants_info.filter(status=settings.OPPORTUNITIES_CH_APPLICANT_REJECTED).count(),
            5)
        self.assertEqual(
            opp.applicants_info.filter(status=settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_READY).count(),
            1)
        self.assertIsNotNone(opp.created_by)
        self.assertIsNotNone(opp.sent_at)
        self.assertEqual(
            opp.users_tagged.count(), 0)
        self.assertEqual(opp.files.count(), 1)
        self.assertEqual(opp.applicants_selected.first().feedbacks.count(), 1)

    @requests_mock.Mocker()
    def test_migrate_fixed(self, mock_request):
        # PREPARE DATA

        self.init_mock(mock_request)
        self.setup_username_credentials()
        group = FakeOpportunityGroupFactory.create(
            related_uuid=uuid.uuid4(),
            budgets=[
                {
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_EUR,
                    'budget': '{}.0'.format(int(faker.numerify()))
                },
                {
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_EXOS,
                    'budget': '{}.0'.format(int(faker.numerify()))
                },
            ]
        )
        users = [
            '97776e09-5cbe-47ea-9433-7c5d71367191',
            'd67851fb-2dec-4974-8ad5-d090739cb532',
        ]
        for user_uuid in users:
            user = User()
            user.uuid = user_uuid
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)

        example_data = {
            'group': group.id.__str__(),
            'title': 'Feedback and guidance on initiatives',
            'description': 'Two initiatives - Initiative  1: ',
            'keywords': [{'name': 'AI'}],
            'deadline_date': '2019-11-13',
            'slug': 'feedback-and-guidance-on-initiatives',
            'mode': 'L',
            'uuid': '1e915064-8f21-4eac-a470-5d840703f1c7',
            'target': 'F',
            'users_tagged': [{'user': '97776e09-5cbe-47ea-9433-7c5d71367191'}],
            'applicants': [{
                'user': '97776e09-5cbe-47ea-9433-7c5d71367191',
                'summary': None,
                'status': 'B'}
            ],
            'created': '2019-11-11T12:51:32.894194+00:00',
            'history': [
                {
                    'created': '2019-11-11T12:52:29.176673+00:00',
                    'status': 'R',
                    'user': 'd67851fb-2dec-4974-8ad5-d090739cb532'},
                {
                    'created': '2019-11-11T12:51:32.911983+00:00',
                    'status': 'X',
                    'user': 'd67851fb-2dec-4974-8ad5-d090739cb532'
                }
            ],
            'status': 'R'}

        url = reverse('api:migrate')

        # DO ACTION
        response = self.client.post(url, data=example_data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opp = models.Opportunity.objects.get(group=group)
        self.assertEqual(opp.uuid.__str__(), example_data.get('uuid'))
        self.assertEqual(opp.group, group)
        self.assertTrue(opp.is_tagged)
        self.assertEqual(
            opp.applicants_info.filter(status=settings.OPPORTUNITIES_CH_APPLICANT_REQUESTED).count(),
            1)
        self.assertIsNotNone(opp.created_by)
        self.assertIsNotNone(opp.sent_at)
        self.assertEqual(
            opp.users_tagged.count(), 1)
