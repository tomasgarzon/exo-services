from django.conf import settings
from django.urls import reverse
from django.test import TestCase

from rest_framework import status

from consultant.faker_factories import FakeConsultantFactory
from test_utils.test_case_mixins import UserTestMixin


class TestApiConsent(UserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.consultant = FakeConsultantFactory(
            user=self.user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)

    def test_image_consent_ok(self):
        # PREPARE DATA
        url = reverse('api:consultant:consent')
        self.client.login(
            username=self.consultant.user.username,
            password='123456')

        # DO ACTION
        response = self.client.post(
            url,
            data={'value': True}
        )

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    def test_consent_bad_request(self):
        # PREPARE DATA
        url = reverse('api:consultant:consent')
        self.client.login(
            username=self.consultant.user.username,
            password='123456')

        # DO ACTION
        response = self.client.post(
            url,
            data={'value': 25}
        )

        # ASSERTS
        self.assertEqual(response.status_code, 400)

    def test_consent_forbidden(self):
        # PREPARE DATA
        self.create_user()

        url = reverse('api:consultant:consent')
        self.client.login(
            username=self.user.username,
            password='123456')

        # DO ACTION
        response = self.client.post(
            url,
            data={'value': True}
        )

        # ASSERTS
        self.assertEqual(response.status_code, 403)
