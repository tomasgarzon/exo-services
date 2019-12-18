import uuid
import requests_mock

from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from exo_role.models import ExORole, CertificationRole

from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin

from .. import models
from .test_mixin import request_mock_account, OpportunityTestMixin


class OpportunityGroupAPITest(
        UserTestMixin,
        OpportunityTestMixin,
        APITestCase):

    def setUp(self):
        self.create_user()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    def get_data(self, user_uuid):
        managers = [self.get_user().uuid.__str__() for _ in range(4)]
        managers.append(user_uuid)
        return {
            'exo_role': ExORole.objects.get(code=settings.EXO_ROLE_CODE_OTHER_OTHER),
            'certification_required': CertificationRole.objects.get(
                code=settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS),
            'entity': faker.name(),
            'duration_unity': settings.OPPORTUNITIES_DURATION_UNITY_HOUR,
            'duration_value': 1,
            'total': 10,
            'origin': settings.OPPORTUNITIES_CH_GROUP_TEAM,
            'related_uuid': uuid.uuid4().__str__(),
            'managers': managers,
            'budgets': [
                {
                    'budget': '222',
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_DOLLAR
                }, {
                    'budget': '1',
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_EXOS
                }
            ],
        }

    @requests_mock.Mocker()
    def test_create_group(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user_uuid = uuid.uuid4().__str__()
        data = self.get_data(user_uuid)
        data['exo_role'] = data['exo_role'].code
        data['certification_required'] = data['certification_required'].code
        url = reverse('api:group-list')
        self.setup_username_credentials()
        request_mock_account.add_mock(
            get_user_model()(uuid=user_uuid), is_consultant=False, is_superuser=True)

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(models.OpportunityGroup.objects.count(), 1)
        self.assertIsNotNone(response.json().get('uuid'))
        self.assertEqual(
            len(response.json().get('managers')), 5)

    @requests_mock.Mocker()
    def test_update_group(self, mock_request):
        # PREPARE DATA
        user_uuid = uuid.uuid4().__str__()
        data = self.get_data(user_uuid)
        self.init_mock(mock_request)
        managers = data.pop('managers')
        group = models.OpportunityGroup.objects.create(**data)
        group.managers.add(
            *get_user_model().objects.filter(uuid__in=managers))
        request_mock_account.add_mock(
            get_user_model()(uuid=user_uuid), is_consultant=False, is_superuser=True)
        url = reverse('api:group-detail', kwargs={'uuid': group.uuid.__str__()})
        self.setup_username_credentials()
        data['total'] = 5
        data['managers'] = managers[1:]
        data['exo_role'] = data['exo_role'].code
        data['certification_required'] = data['certification_required'].code

        # DO ACTION
        response = self.client.put(url, data)

        # ASSERTS
        group.refresh_from_db()

        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(models.OpportunityGroup.objects.count(), 1)
        self.assertIsNotNone(response.json().get('uuid'))
        self.assertEqual(group.total, data['total'])
        self.assertEqual(group.managers.count(), len(data['managers']))

    @requests_mock.Mocker()
    def test_filtering_groups(self, mock_request):
        # PREPARE DATA
        data = self.get_data(user_uuid=None)
        self.init_mock(mock_request)
        data.pop('managers')
        models.OpportunityGroup.objects.create(**data)
        url = reverse('api:group-list')
        self.setup_username_credentials()

        # DO ACTION
        list_url = url + '?related_uuid={}'.format(data['related_uuid'])
        empty_list_url = url + '?related_uuid={}'.format(uuid.uuid4().__str__())
        response = self.client.get(list_url)
        response_empty = self.client.get(empty_list_url)

        # ASSERTS
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(len(response_empty.json()), 0)
