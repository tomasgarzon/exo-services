import factory

from factory import django

from utils.faker_factory import faker

from ..models import AssignmentResourceItem


class FakeAssignmentResourceItemFactory(django.DjangoModelFactory):

    class Meta:
        model = AssignmentResourceItem

    assignment_resource = factory.SubFactory('assignment.faker_factories.assignment.FakeAssignmentResourceFactory')
    name = factory.LazyAttribute(lambda x: faker.word())
    description = factory.LazyAttribute(lambda x: faker.text())
    thumbnail = factory.LazyAttribute(lambda x: faker.url())
    iframe = ''
    link = factory.LazyAttribute(lambda x: faker.url())
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
