# Third Party Library
import factory
from factory import django

from utils.faker_factory import faker

from .models import Keyword


class FakeKeywordFactory(django.DjangoModelFactory):

    """
        Creates a fake keyword.
    """

    class Meta:
        model = Keyword

    name = factory.LazyAttribute(lambda x: faker.word() + faker.numerify())
    public = True
