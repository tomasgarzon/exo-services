from django.urls import reverse

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from utils.faker_factory import faker
from exo_messages.models import Message


class UserProfileEmailAPITests(
        SuperUserTestMixin, DjangoRestFrameworkTestCase
):

    def setUp(self):
        self.create_superuser()

    def test_change_email_with_superuser(self):
        consultant = FakeConsultantFactory.create()
        self.client.login(
            username=self.super_user.username,
            password='123456',
        )
        url = reverse(
            'api:profile:change-email',
            kwargs={'pk': consultant.user.pk},
        )
        data = {}
        new_email = faker.email()
        data['email'] = new_email
        response = self.client.put(url, data=data, format='json')
        consultant.user.refresh_from_db()

        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(consultant.user.email, new_email)

        # Should generate NO MESSAGE for the user
        self.assertEqual(
            Message.objects.filter_by_user(consultant.user).count(),
            0,
        )

    def test_change_email_pending(self):
        consultant = FakeConsultantFactory.create(user__is_active=True)
        previous_email = consultant.user.email
        self.client.login(
            username=consultant.user.email,
            password=consultant.user.short_name,
        )
        url = reverse(
            'api:profile:change-email',
            kwargs={'pk': consultant.user.pk},
        )
        data = {}
        data['email'] = faker.email()
        response = self.client.put(url, data=data, format='json')

        consultant.user.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(consultant.user.email, previous_email)
        self.assertEqual(
            Message.objects.filter_by_user(
                consultant.user,
            ).count(), 1,
        )

    def test_change_email_invalid(self):
        consultant = FakeConsultantFactory.create()
        self.client.login(
            username=self.super_user.username,
            password='123456',
        )
        url = reverse(
            'api:profile:change-email',
            kwargs={'pk': consultant.user.pk},
        )
        data = {'email': self.super_user.email}
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))
        self.assertIsNotNone(response.data.get('email'))

    def test_change_previous_email(self):
        consultant = FakeConsultantFactory.create()
        previous_email = consultant.user.email
        self.client.login(
            username=self.super_user.username,
            password='123456',
        )
        consultant.user.add_email_address(faker.email(), True)
        url = reverse(
            'api:profile:change-email',
            kwargs={'pk': consultant.user.pk},
        )
        data = {}
        data['email'] = previous_email
        response = self.client.put(url, data=data, format='json')
        consultant.user.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(consultant.user.email, previous_email)
        self.assertEqual(
            Message.objects.filter_by_user(
                consultant.user,
            ).count(), 0,
        )
