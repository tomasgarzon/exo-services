from django.urls import reverse

from rest_framework import status

from consultant.faker_factories import FakeConsultantFactory
from utils.faker_factory import faker
from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from test_utils import TestInboxMixin


class UserRequestContactAPITests(
        SuperUserTestMixin,
        TestInboxMixin,
        DjangoRestFrameworkTestCase):

    def test_contact(self):
        # PREPARE DATA
        self.clear_inbox()
        consultant1 = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456')
        consultant2 = FakeConsultantFactory.create(user__is_active=True)

        data = {
            'user': consultant2.user.pk,
            'comment': faker.text()
        }

        url = reverse('api:accounts:request-contact')

        # DO ACTION
        self.client.login(username=consultant1.user.email, password='123456')
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.get_inbox_length(), 1)
        self.assertEqual(
            self.get_inbox_recipients_email_list(),
            [consultant2.user.email])
