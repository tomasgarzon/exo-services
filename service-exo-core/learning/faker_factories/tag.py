# Third Party Library
import factory
from factory import django

from utils.faker_factory import faker

from ..models import Tag


class FakeTagFactory(django.DjangoModelFactory):

    """
        Creates a fake consultant.
    """

    class Meta:
        model = Tag

    name = factory.LazyAttribute(lambda x: faker.word())
