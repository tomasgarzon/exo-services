import re

from django.conf import settings

from auth_uuid.jwt_helpers import _build_jwt
from auth_uuid.tests.test_mixin import RequestMockAccount

from ..faker_factories import FakeJobFactory


class JobTestMixin:

    def create_job(self, user):
        return FakeJobFactory.create(user=user)

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
