import factory

from factory import django

from utils.faker_factory import faker

from ..models import AssignmentText


class FakeAssignmentTextFactory(django.DjangoModelFactory):

    class Meta:
        model = AssignmentText

    block = factory.SubFactory('assignment.faker_factories.assignment.InformationBlockFactory')
    text = factory.LazyAttribute(lambda x: faker.word())
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
