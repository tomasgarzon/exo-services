import factory

from factory import django

from utils.faker_factory import faker

from ..models import ExOHub


class FakeExOHubFactory(django.DjangoModelFactory):

    class Meta:
        model = ExOHub

    name = factory.LazyAttribute(lambda x: faker.word())
    order = 1
