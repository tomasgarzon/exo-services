# Third Party Library
import factory
from factory import django

from utils.faker_factory import faker

from .models import Language


class FakeLanguageFactory(django.DjangoModelFactory):

    class Meta:
        model = Language

    name = factory.LazyAttribute(lambda x: faker.word())
