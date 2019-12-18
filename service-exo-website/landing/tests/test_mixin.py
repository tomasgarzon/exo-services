import re

from django.conf import settings

from auth_uuid.jwt_helpers import _build_jwt
from auth_uuid.tests.test_mixin import RequestMockAccount


class TestMixin:

    def init_mock(self, m):
        matcher = re.compile('{}/api/accounts/me/'.format(settings.EXOLEVER_HOST))
        m.register_uri(
            'GET',
            matcher,
            json=mock_callback)

    def setup_credentials(self, user):
        token = _build_jwt(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)


request_mock_account = RequestMockAccount()


def mock_callback(request, context):
    uuid = request.path.split('/')[-2]
    return request_mock_account.get_request(uuid)
