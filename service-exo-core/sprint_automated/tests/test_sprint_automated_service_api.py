from django.urls import reverse
from django.conf import settings

from rest_framework import status

from customer.faker_factories import FakeCustomerFactory
from project.models import Step
from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker
from learning.models import MicroLearning

from ..models import SprintAutomated
from ..faker_factories import FakeSprintAutomatedFactory


class TestAPICreateSprintAutomated(SuperUserTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        self.create_superuser()

    def test_api_create_sprint_automated(self):
        # PREPARE DATA
        url = reverse('api:project:create-service')
        customer = FakeCustomerFactory.create()
        data = {
            'type_project': settings.PROJECT_CH_TYPE_SPRINT_AUTOMATED,
            'name': faker.name(),
            'description': faker.text(),
            'customer': customer.id,
        }
        self.client.login(username=self.super_user.username, password='123456')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        sprint = SprintAutomated.objects.get(id=response.data.get('id'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sprint.name, data.get('name'))
        self.assertEqual(sprint.description, data.get('description'))
        self.assertEqual(sprint.customer, customer)

    def test_steps_creation_for_sprint_automated(self):
        # DO ACTION
        sprint = FakeSprintAutomatedFactory.create(start=None)

        # ASSERTS
        project = sprint.project_ptr
        periods = Step.objects.filter_by_project(project)
        self.assertEqual(project.duration, settings.SPRINT_AUTOMATED_STEPS_COUNT)
        self.assertEqual(periods.count(), settings.SPRINT_AUTOMATED_STEPS_COUNT)
        self.assertEqual(project.lapse, settings.PROJECT_LAPSE_PERIOD)

        for period in periods:
            self.assertIsNone(period.start)
            self.assertIsNone(period.end)
            self.assertIsNotNone(period.name)
            self.assertIsNotNone(period.index)

        # Currently, our populator only have quiz for 3 steps
        self.assertEqual(
            MicroLearning.objects.filter(step_stream__step__project=project).count(),
            20)
