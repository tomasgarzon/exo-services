import re
import datetime
from datetime import timedelta

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import Permission
from django.shortcuts import get_object_or_404

from exo_role.models import ExORole
from auth_uuid.jwt_helpers import _build_jwt
from auth_uuid.tests.test_mixin import RequestMockAccount

from languages.models import Language
from utils.faker_factory import faker

from ..faker_factories import (
    FakeOpportunityFactory,
    FakeQuestionFactory,
)


class OpportunityTestMixin:
    def get_sow_data(self):
        return {
            'title': faker.text(),
            'description': faker.text(),
            'mode': settings.OPPORTUNITIES_CH_MODE_DEFAULT,
            'location': faker.city(),
            'start_date': datetime.date.today(),
            'end_date': datetime.date.today() + datetime.timedelta(days=20),
            'duration_unity': settings.OPPORTUNITIES_DURATION_UNITY_DAY,
            'duration_value': 2,
            'start_time': faker.time(),
            'timezone': faker.timezone(),
            'entity': faker.name(),
            'budgets': [
                {
                    'budget': '222',
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_DOLLAR
                }
            ],
        }

    def get_api_data(self, users=[]):
        keywords = [
            {'name': faker.word() + faker.numerify()},
            {'name': faker.word() + faker.numerify()},
        ]
        data = {
            'title': faker.word(),
            'description': faker.text(),
            'mode': settings.OPPORTUNITIES_CH_MODE_ONSITE,
            'location': '{}, {}'.format(faker.city(), faker.country()),
            'exo_role': ExORole.objects.get(code=settings.EXO_ROLE_CODE_OTHER_OTHER).code,
            'other_category_name': faker.word(),
            'other_role_name': faker.word(),
            'certification_required': None,
            'due_date': timezone.now().date(),
            'deadline_date': (timezone.now() + timedelta(days=10)).date(),
            'duration_unity': settings.OPPORTUNITIES_DURATION_UNITY_DAY,
            'duration_value': 2,
            'num_positions': 2,
            'keywords': keywords,
            'entity': faker.company(),
            'files': [{
                'filestack_status': 'Stored',
                'url': 'https://cdn.filestackcontent.com/Lr59QG8oQRWliC6x70cx',
                'filename': 'gato.jpg',
                'mimetype': 'image/jpeg'}],
            'budgets': [
                {
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_EUR,
                    'budget': '{}.0'.format(int(faker.numerify()))
                },
                {
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_EXOS,
                    'budget': '{}.0'.format(int(faker.numerify()))
                },
            ]
        }
        if users:
            data['target'] = settings.OPPORTUNITIES_CH_TARGET_FIXED
            data['users_tagged'] = [
                {'user': user.uuid.__str__()} for user in users
            ]
        return data

    def add_marketplace_permission(self, user):
        perm = settings.AUTH_USER_PERMS_MARKETPLACE_FULL
        permission = get_object_or_404(
            Permission,
            codename=perm)
        user.user_permissions.add(permission)

    def create_opportunity(
        self, user=None, questions=3, num_positions=3, target=None,
        duration_unity=None, role=None, group=None,
    ):

        if not user:
            user = self.super_user
        data = {
            'user_from': user,
            'num_positions': num_positions,
        }
        if target:
            data['target'] = target

        if duration_unity:
            data['duration_unity'] = duration_unity

        if role:
            data['exo_role'] = role
        if group:
            data['group'] = group
        opportunity = FakeOpportunityFactory.create(**data)
        languages = [
            Language.objects.create(name=faker.word() + faker.numerify()) for _ in range(2)]
        opportunity.languages.add(*languages)
        FakeQuestionFactory.create_batch(size=questions, opportunity=opportunity)
        return opportunity

    def init_mock(self, m):
        matcher = re.compile('{}/api/accounts/me/'.format(settings.EXOLEVER_HOST))
        m.register_uri(
            'GET',
            matcher,
            json=mock_callback)
        m.register_uri(
            'GET',
            re.compile(
                '{}/api/consultant/consultant/can-receive-opportunities/'.format(
                    settings.EXOLEVER_HOST)),
            json=[])
        m.register_uri(
            'GET',
            re.compile(
                '{}/api/accounts/groups/{}/'.format(
                    settings.EXOLEVER_HOST,
                    settings.OPPORTUNITIES_DELIVERY_MANAGER_GROUP)),
            json={'user_set': []})
        m.register_uri(
            'POST',
            re.compile(
                '{}{}api/mail/'.format(
                    settings.EXOLEVER_HOST,
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
