from django.urls import reverse

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from utils.faker_factory import faker
from consultant.models.consultant_profile_requirement import (
    ConsultantProfileRequirement
)


class ProfileAboutYouAPITests(SuperUserTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_change_profile_summary(self):
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:about-you',
            kwargs={'pk': consultant.user.pk},
        )
        data = {
            'bio_me': faker.paragraph(),
            'linkedin': faker.word(),
            'website': faker.url(),
            'twitter': faker.word(),
        }
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        consultant.user.refresh_from_db()
        user = consultant.user
        self.assertEqual(user.bio_me, data['bio_me'])
        profile = ConsultantProfileRequirement()
        self.assertTrue(
            profile.get_consultant_requirement(
                ConsultantProfileRequirement.KEY_SUMMARY,
                consultant,
            ),
        )
        self.assertEqual(user.linkedin.value, data['linkedin'])
        self.assertEqual(user.twitter.value, data['twitter'])
        self.assertEqual(user.website.value, data['website'])
