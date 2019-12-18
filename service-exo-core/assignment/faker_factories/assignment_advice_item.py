import factory

from factory import django

from utils.faker_factory import faker

from ..models import AssignmentAdviceItem


class FakeAssignmentAdviceItemFactory(django.DjangoModelFactory):

    class Meta:
        model = AssignmentAdviceItem

    assignment_advice = factory.SubFactory('assignment.faker_factories.assignment.FakeAssignmentAdviceFactory')
    description = factory.LazyAttribute(lambda x: faker.word())
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
