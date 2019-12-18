from django import test
from django.utils import timezone

from test_utils.test_case_mixins import SuperUserTestMixin
from customer.faker_factories import FakeCustomerFactory
from utils.faker_factory import faker

from ..models import Project


class ProjectManagerTest(SuperUserTestMixin, test.TestCase):

    def setUp(self):
        self.create_superuser()
        super().setUp()

    def test_create_sprint(self):
        # Prepare data
        name = faker.first_name()
        start = timezone.now()
        customer = FakeCustomerFactory.create()

        # Do action
        sprint = Project.objects.create_sprint_automated(self.super_user, name, start, customer, duration=1)

        # Asserts
        self.assertIsNotNone(sprint)
