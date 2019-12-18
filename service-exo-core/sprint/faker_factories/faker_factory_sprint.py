from django.conf import settings

import factory

from project.faker_factories.faker_factory_project import FakeProjectFactory
from utils.faker_factory import faker

from ..models import Sprint


class FakeSprintAutomatedFactory(FakeProjectFactory):

    class Meta:
        model = Sprint

    challenges = factory.LazyAttribute(lambda x: faker.paragraph())
    goals = factory.LazyAttribute(lambda x: faker.paragraph())
    duration = 10
    lapse = settings.PROJECT_LAPSE_WEEK
