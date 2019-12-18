from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from assignment.models import AssignmentStep
from assignment.tests.assignments_mixin import AssignmentsMixin
from project.models import Step
from test_utils.test_case_mixins import SuperUserTestMixin

from ..faker_factories import GenericProjectFactory


class TestGenericProjectSettings(
        AssignmentsMixin, SuperUserTestMixin, TestCase):

    def setUp(self):
        self.create_superuser()

    def prepare_data(self):
        self.generic_project = GenericProjectFactory.create()
        self.client.login(username=self.super_user.username, password='123456')

    def test_generic_project_steps_creation(self):
        # DO ACTION
        self.prepare_data()

        # ASSERTS
        steps = Step.objects.filter_by_project(self.generic_project.project_ptr)
        self.assertEqual(steps.count(), self.generic_project.duration)

    def test_generic_project_settings_empty_version(self):
        # PREPARE DATA
        self.prepare_data()
        data = {
            'version': '',
        }

        # DO ACTION
        response = self.client.post(reverse('project:project:settings', args=[self.generic_project.pk]), data=data)

        # ASSERTS
        self.assertTrue(response.context_data.get('form').errors.get('version'))

    def test_generic_project_settings_update_version(self):
        # PREPARE DATA
        self.prepare_data()
        data = {
            'version': settings.PROJECT_CH_VERSION_DEFAULT,
            'advisor_request_enabled': True,
            'num_tickets_per_team': 5,
            'tickets_price': 200,
            'tickets_currency': settings.OPPORTUNITIES_CH_CURRENCY_EXOS,
        }

        # DO ACTION
        self.client.post(reverse('project:project:settings', args=[self.generic_project.pk]), data=data)

        # ASSERTS
        self.assertEqual(self.generic_project.settings.version, settings.PROJECT_CH_VERSION_2)

    def test_generic_project_settings_update_template_assignments(self):
        # PREPARE DATA
        self.prepare_data()
        Step.objects.update_steps(self.generic_project.project_ptr)
        data = {
            'version': settings.PROJECT_CH_VERSION_DEFAULT,
            'template_assignments': settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK,
            'advisor_request_enabled': True,
            'num_tickets_per_team': 5,
            'tickets_price': 200,
            'tickets_currency': settings.OPPORTUNITIES_CH_CURRENCY_EXOS,
        }
        self.client.login(username=self.super_user.username, password='123456')

        # ASSERTS
        self.assertFalse(
            AssignmentStep.objects.filter_by_project(self.generic_project.project_ptr).exists())

        # DO ACTION
        self.client.post(reverse('project:project:settings', args=[self.generic_project.pk]), data=data)

        # ASSERTS
        self.assertEqual(
            self.generic_project.get_assignments_template(),
            settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK)
        self.assertTrue(
            AssignmentStep.objects.filter_by_project(self.generic_project.project_ptr).exists())

    def test_generic_project_settings_clean_template_assignments(self):
        # PREPARE DATA
        self.prepare_data()
        Step.objects.update_steps(self.generic_project.project_ptr)
        self.populate_assignments_version_2(
            self.generic_project,
            settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK)
        project_settings = self.generic_project.settings
        project_settings.template_assignments = settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK
        project_settings.save()
        data = {
            'version': settings.PROJECT_CH_VERSION_DEFAULT,
            'template_assignments': '',
            'advisor_request_enabled': True,
            'num_tickets_per_team': 5,
            'tickets_price': 200,
            'tickets_currency': settings.OPPORTUNITIES_CH_CURRENCY_EXOS,
        }

        # ASSERTS
        self.assertTrue(AssignmentStep.objects.filter_by_project(self.generic_project.project_ptr).exists())

        self.client.login(username=self.super_user.username, password='123456')
        # DO ACTION
        self.client.post(reverse('project:project:settings', args=[self.generic_project.pk]), data=data)

        # ASSERTS
        self.assertEqual(self.generic_project.get_assignments_template(), '')
        self.assertFalse(AssignmentStep.objects.filter_by_project(self.generic_project.project_ptr).exists())
