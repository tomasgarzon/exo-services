import re
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model

from auth_uuid.jwt_helpers import _build_jwt
from auth_uuid.tests.test_mixin import RequestMockAccount


class UserTestMixin:

    def create_user(self):
        self.user = get_user_model().objects.create(
            uuid=uuid.uuid4(),
            is_active=True,
        )
        self.user.set_password('123456')
        self.user.save()

    def create_super_user(self):
        self.super_user = get_user_model().objects.create(
            uuid=uuid.uuid4(),
            is_active=True,
            is_superuser=True,
            is_staff=True
        )
        self.super_user.set_password('123456')
        self.super_user.save()

    def get_user(self):
        user = get_user_model().objects.create(
            uuid=uuid.uuid4(),
            is_active=True,
        )
        user.set_password('123456')
        user.save()
        return user

    def init_mock(self, m):
        matcher = re.compile('{}/api/accounts/me/'.format(settings.EXOLEVER_HOST))
        m.register_uri(
            'GET',
            matcher,
            json=mock_callback)
        m.register_uri(
            'POST',
            re.compile(
                '{}/api/mail/'.format(
                    settings.SERVICE_EXO_MAIL_HOST)),
            json={})

    def setup_credentials(self, user):
        token = _build_jwt(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def setup_username_credentials(self):
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)


request_mock_account = RequestMockAccount()


def mock_callback(request, context):
    uuid = request.path.split('/')[-2]
    return request_mock_account.get_request(uuid)
