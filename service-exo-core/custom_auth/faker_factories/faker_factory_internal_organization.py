import factory

from factory import django

from utils.faker_factory import faker

from ..models import InternalOrganization


class FakeInternalOrganizationFactory(django.DjangoModelFactory):

    class Meta:
        model = InternalOrganization

    name = factory.LazyAttribute(lambda x: faker.name())
