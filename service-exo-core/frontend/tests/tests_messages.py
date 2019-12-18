from django.urls import reverse
from django.contrib import messages

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin
from utils.faker_factory import faker


class MessagesAPITest(
        UserTestMixin,
        DjangoRestFrameworkTestCase
):

    def setUp(self):
        self.create_user()

    def test_messages_ok(self):
        self.client.login(username=self.user.username, password='123456')
        messages.success(self.client.request().wsgi_request, faker.text())
        url = reverse('api:messages')
        data = {}
        response = self.client.get(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))

    def test_messages_not_authenticated(self):
        url = reverse('api:messages')
        data = {}
        response = self.client.get(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data, [])
