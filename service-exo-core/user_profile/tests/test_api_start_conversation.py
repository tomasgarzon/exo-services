from django.urls import reverse
from django.conf import settings

from rest_framework import status
import requests_mock

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from utils.faker_factory import faker


class StartConversationAPITests(
        UserTestMixin,
        DjangoRestFrameworkTestCase):
    def setUp(self):
        self.create_user()

    @requests_mock.Mocker()
    def test_create_conversation(self, mocker):
        url = '{}{}api/conversations/create-group/'.format(
            settings.EXOLEVER_HOST,
            settings.SERVICE_CONVERSATIONS_HOST)
        mocker.post(
            url, json={})
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
        )
        self.client.login(
            username=self.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:start-conversation',
            kwargs={'pk': consultant.user.pk},
        )
        data = {
            'message': faker.word(),
            'files': []
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
