import factory
import factory.fuzzy

from utils.faker_factory import faker

from ..models import Answer


class FakeAnswerFactory(factory.django.DjangoModelFactory):

    response = factory.LazyAttribute(lambda x: faker.boolean())

    class Meta:
        model = Answer
