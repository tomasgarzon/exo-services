from django.urls import reverse

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin
from utils.faker_factory import faker
from consultant.faker_factories import FakeConsultantFactory


class ProfileConsultantVideoAPITests(UserTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        self.create_user()

    def test_update_consultant_video_profile_from_url(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        self.client.login(username=consultant.user.email, password=consultant.user.short_name)
        url = reverse('api:profile:update-profile-video', args=[consultant.pk])
        data = {'video_url': faker.url()}

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        consultant.exo_profile.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(consultant.exo_profile.video_url, data.get('video_url'))

    def test_update_consultant_video_profile_with_empty_url(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        self.client.login(username=consultant.user.email, password=consultant.user.short_name)
        url = reverse('api:profile:update-profile-video', args=[consultant.pk])
        data = {'video_url': ''}

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    def test_update_consultant_video_profile_with_no_perms_edit_consultant_profile(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        self.client.login(username=self.user.email, password='123456')
        url = reverse('api:profile:update-profile-video', args=[consultant.pk])
        data = {'video_url': faker.url()}

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))
