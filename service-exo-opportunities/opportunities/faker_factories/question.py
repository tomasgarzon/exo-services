import factory
import factory.fuzzy

from utils.faker_factory import faker

from ..models import Question


class FakeQuestionFactory(factory.django.DjangoModelFactory):

    title = factory.LazyAttribute(lambda x: faker.text())

    class Meta:
        model = Question
