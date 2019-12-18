from django.urls import reverse
from django.test import TestCase

from mock import patch
from rest_framework import status

from test_utils.test_case_mixins import SuperUserTestMixin
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from sprint.forms.sprint import SprintSimpleForm
from utils.faker_factory import faker

from ..conf import settings


class ServiceEditFormTest(
        SuperUserTestMixin,
        TestCase
):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    @patch('project.signals_define.edit_project_start_date.send')
    def test_edit_service_sprint_from_django_form(self, mock):
        # PREPARE DATA
        sprint = FakeSprintAutomatedFactory()
        new_date = '2013-01-01 10:00:00'
        sprint_form = SprintSimpleForm(instance=sprint)
        data = sprint_form.initial
        data['start'] = new_date
        data['agenda'] = ''
        data['location'] = faker.city()
        data['timezone'] = faker.timezone()
        data['place_id'] = faker.pyint()
        url = reverse('project:project:dashboard', kwargs={'project_id': sprint.id})
        self.client.login(username=self.super_user.username, password='123456')

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    def test_edit_project_settings_form(self):
        # PREPARE DATA
        self.client.login(username=self.super_user.username, password='123456')
        sprint = FakeSprintAutomatedFactory()
        url = reverse('project:project:settings', args=[sprint.pk])

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        initial = response.context.get('form').initial
        self.assertFalse(initial['send_welcome_consultant'])
        self.assertFalse(initial['send_welcome_participant'])
        self.assertEqual(initial['fix_password'], '')
        self.assertFalse(initial['participant_step_feedback_enabled'])
        self.assertTrue(initial['directory_enabled'])

        # PREPARE DATA
        new_data = {
            'send_welcome_consultant': True,
            'send_welcome_participant': True,
            'fix_password': faker.name(),
            'participant_step_feedback_enabled': False,
            'version': settings.PROJECT_CH_VERSION_DEFAULT,
            'directory_enabled': False,
            'advisor_request_enabled': True,
            'num_tickets_per_team': 5,
            'tickets_price': 200,
            'tickets_currency': settings.OPPORTUNITIES_CH_CURRENCY_EXOS,
        }

        # DO ACTION
        response = self.client.post(url, data=new_data)

        # ASSERTS
        sprint_settings = sprint.settings
        self.assertTrue(sprint_settings.launch['send_welcome_consultant'])
        self.assertTrue(sprint_settings.launch['send_welcome_participant'])
        self.assertEqual(
            sprint_settings.launch['fix_password'],
            new_data.get('fix_password'))
        self.assertFalse(sprint_settings.participant_step_feedback_enabled)
        self.assertFalse(sprint_settings.directory)
