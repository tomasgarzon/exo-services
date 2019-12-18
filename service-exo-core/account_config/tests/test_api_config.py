from django.urls import reverse
from django.conf import settings

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from consultant.faker_factories import FakeConsultantFactory

from ..models import ConfigParam


class ConfigParamTestCase(DjangoRestFrameworkTestCase):

    def setUp(self):
        self.user = FakeUserFactory.create(
            password='123456', is_active=True)
        self.consultant = FakeConsultantFactory.create(
            user__password='123456', user__is_active=True)

    def assertConfigData(self, data):
        for k in data:
            self.assertIsNotNone(k['value'])
            self.assertIsNotNone(k['group'])
            self.assertIsNotNone(k['name'])

    def test_config_user(self):
        # PREPARE DATA
        url = reverse(
            'api:account-config:config-param',
            kwargs={'pk': self.user.pk})
        self.client.login(
            username=self.user.username, password='123456')
        total_expected = 0
        for _, items in settings.ACCOUNT_CONF_GROUPS.get('exo_accounts.User').items():
            total_expected += len(items)

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), total_expected)
        self.assertConfigData(response.json())

    def test_config_user_by_uuid(self):
        # PREPARE DATA
        url = reverse(
            'api:account-config:config-param-uuid',
            kwargs={'user_uuid': self.user.uuid.__str__()})
        self.client.login(
            username=self.user.username, password='123456')
        total_expected = 0
        for _, items in settings.ACCOUNT_CONF_GROUPS.get('exo_accounts.User').items():
            total_expected += len(items)

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

        self.assertEqual(
            len(response.data),
            total_expected)
        self.assertConfigData(response.json())

    def test_config_consultant(self):
        # PREPARE DATA
        url = reverse(
            'api:account-config:config-param',
            kwargs={'pk': self.consultant.user.pk})
        self.client.login(
            username=self.consultant.user.username, password='123456')
        total_expected = 0
        for _, items in settings.ACCOUNT_CONF_GROUPS.get('consultant.Consultant').items():
            total_expected += len(items)

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), total_expected)
        for k in response.data:
            if k['name'] in ['new_question_from_project']:
                self.assertIsNone(k['value'])
            else:
                self.assertIsNotNone(k['value'])
            self.assertIsNotNone(k['group'])
            self.assertIsNotNone(k['name'])

    def test_update_config_param(self):
        # PREPARE DATA
        config_param = ConfigParam.objects.first()
        url = reverse(
            'api:account-config:config-param-update',
            kwargs={
                'pk': self.user.pk,
                'config_pk': config_param.pk})
        self.client.login(
            username=self.user.username, password='123456')

        data = {
            'value': 'True'
        }

        # DO ACTION
        response = self.client.post(url, data=data)
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(eval(response.data['value']))
        self.assertTrue(config_param.get_value_for_agent(self.user))
