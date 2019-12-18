import re
import uuid

from django.conf import settings

from auth_uuid.jwt_helpers import _build_jwt
from auth_uuid.tests.test_mixin import RequestMockAccount

from utils.faker_factory import faker


class GeneralModel:
    uuid = None

    def __init__(self, uuid):
        self.uuid = str(uuid)


class ConversationMixin:
    def generate_fake_user_data(self, user):
        return {
            'user': user,
            'name': faker.name(),
            'profile_picture': faker.image_url(),
            'profile_url': faker.uri(),
            'short_title': faker.word()
        }

    def create_object(self, user=None):
        if not user:
            user = self.super_user
        generic_object = GeneralModel(uuid.uuid4())
        generic_object.user_from = user
        return generic_object

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


request_mock_account = RequestMockAccount()


def mock_callback(request, context):
    uuid = request.path.split('/')[-2]
    return request_mock_account.get_request(uuid)
