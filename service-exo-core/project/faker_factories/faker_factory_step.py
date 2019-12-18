# -*- coding: utf-8 -*-
from factory import fuzzy, django  # noqa
import factory
import random

from utils.faker_factory import faker

from ..models import Step


class FakeStepFactory(django.DjangoModelFactory):

    class Meta:
        model = Step

    project = factory.SubFactory('project.faker_factories.FakeProjectFactory')
    name = factory.LazyAttribute(lambda x: faker.name() + faker.numerify())
    index = factory.LazyAttribute(lambda x: random.randint(1, 20))
