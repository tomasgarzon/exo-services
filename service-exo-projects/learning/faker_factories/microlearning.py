import factory
from factory import django

from utils.faker_factory import faker

from ..models import MicroLearning


class FakeMicroLearningFactory(django.DjangoModelFactory):

    class Meta:
        model = MicroLearning

    typeform_url = factory.LazyAttribute(lambda x: faker.url())
