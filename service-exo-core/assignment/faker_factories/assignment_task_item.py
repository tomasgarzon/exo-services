import factory

from factory import django

from utils.faker_factory import faker

from ..models import AssignmentTaskItem


class FakeAssignmentTaskItemFactory(django.DjangoModelFactory):

    class Meta:
        model = AssignmentTaskItem

    assignment_task = factory.SubFactory('assignment.faker_factories.assignment.FakeAssignmentTaskFactory')
    name = factory.LazyAttribute(lambda x: faker.word())
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
