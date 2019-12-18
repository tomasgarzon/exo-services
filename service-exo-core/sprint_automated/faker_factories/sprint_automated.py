import factory

from django.conf import settings

from project.faker_factories.faker_factory_project import FakeProjectFactory
from utils.faker_factory import faker

from ..models import SprintAutomated


class FakeSprintAutomatedFactory(FakeProjectFactory):

    class Meta:
        model = SprintAutomated

    name = factory.LazyAttribute(lambda x: faker.word())
    description = factory.LazyAttribute(lambda x: faker.text())
    duration = settings.SPRINT_AUTOMATED_STEPS_COUNT
    lapse = settings.PROJECT_LAPSE_PERIOD
    agenda = None
