import factory

from factory import django

from utils.faker_factory import faker

from ..models import Survey


class FakeSurveyFactory(django.DjangoModelFactory):

    class Meta:
        model = Survey

    name = factory.LazyAttribute(lambda x: faker.word())
    slug = factory.LazyAttribute(lambda x: faker.word())
