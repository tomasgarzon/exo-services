import uuid
import re

from django.contrib.auth import get_user_model
from django.conf import settings

from auth_uuid.jwt_helpers import _build_jwt
from auth_uuid.tests.test_mixin import RequestMockAccount


class UserTestMixin:

    def create_user(self):
        self.user = get_user_model().objects.create(
            uuid=uuid.uuid4(),
            is_active=True,
        )
        self.user.set_password('123456')

    def create_super_user(self):
        self.super_user = get_user_model().objects.create(
            uuid=uuid.uuid4(),
            is_active=True,
            is_superuser=True,
            is_staff=True
        )
        self.super_user.set_password('123456')

    def get_user(self, mock_user=False, is_consultant=False, is_superuser=False):
        user = get_user_model().objects.create(
            uuid=uuid.uuid4(),
            is_active=True,
        )
        user.set_password('123456')

        if mock_user:
            request_mock_account.add_mock(
                user,
                is_consultant=is_consultant,
                is_superuser=is_superuser)

        return user

    def update_user_mock(self, user, mocked_data):
        request_mock_account.update_mock(
            str(user.uuid), **mocked_data)


class MockerTestMixin:

    def init_mock(self, m):
        matcher = re.compile('{}/api/accounts/me/'.format(settings.EXOLEVER_HOST))
        m.register_uri(
            'GET',
            matcher,
            json=mock_callback)
        m.register_uri(
            'GET',
            settings.METRIC_URL + '/email/',
            json={'url': 'https://www.google-analytics.com/collect?v=1'})

    def setup_credentials(self, user):
        token = _build_jwt(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def setup_username_credentials(self):
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)


request_mock_account = RequestMockAccount()


def mock_callback(request, context):
    uuid = request.path.split('/')[-2]
    return request_mock_account.get_request(uuid)
