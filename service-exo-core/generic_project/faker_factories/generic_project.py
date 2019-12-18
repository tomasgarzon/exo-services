import factory
import random

from django.conf import settings

from project.faker_factories.faker_factory_project import FakeProjectFactory
from utils.faker_factory import faker

from ..models import GenericProject


class GenericProjectFactory(FakeProjectFactory):

    class Meta:
        model = GenericProject

    name = factory.LazyAttribute(lambda x: faker.word())
    duration = random.randint(1, 100)
    lapse = settings.PROJECT_LAPSE_PERIOD
    agenda = None
