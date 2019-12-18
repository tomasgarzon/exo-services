import factory
import random

from factory import django

from utils.faker_factory import faker

from ..models import SurveyFilled, Question


class FakeSurveyFilledFactory(django.DjangoModelFactory):

    class Meta:
        model = SurveyFilled

    name = factory.LazyAttribute(lambda x: faker.word())
    organization = factory.LazyAttribute(lambda x: faker.word())
    email = factory.LazyAttribute(lambda x: faker.email())
    total = 20

    @factory.post_generation
    def answers(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        answers = []
        for question in Question.objects.all():
            answers.append({
                'question': question,
                'option': random.choice(question.options.all())
            })
        self._fill_answers(answers)
