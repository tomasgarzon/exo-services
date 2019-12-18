from django.urls import reverse

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from utils.faker_factory import faker


class ProfileSummaryAPITests(SuperUserTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_change_profile_summary(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__bio_me=None,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:change-profile-summary',
            kwargs={'pk': consultant.user.pk},
        )
        data = {
            'bio_me': faker.paragraph(),
            'about_me': ','.join(faker.paragraphs()),
        }

        # DO ACTION
        response = self.client.put(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        consultant.user.refresh_from_db()
        user = consultant.user
        self.assertEqual(user.bio_me, data['bio_me'])
        self.assertEqual(user.about_me, data['about_me'])

    def test_change_profile_summary_optional(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:change-profile-summary',
            kwargs={'pk': consultant.user.pk},
        )
        user = consultant.user
        user.about_me = ','.join(faker.paragraphs())
        user.bio_me = faker.paragraph()
        user.save()
        data = {
            'about_me': '',
            'bio_me': '',
        }

        # DO ACTION
        response = self.client.put(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        user.refresh_from_db()
        self.assertEqual(user.bio_me, '')
        self.assertEqual(user.about_me, '')
