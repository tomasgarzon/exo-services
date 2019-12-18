# -*- coding: utf-8 -*-
import factory

from factory import django

from utils.faker_factory import faker

from ..models import Team


class FakeTeamFactory(django.DjangoModelFactory):

    class Meta:
        model = Team

    project = factory.SubFactory('project.faker_factories.FakeProjectFactory')
    name = factory.LazyAttribute(lambda x: faker.word())
    stream = None
    created_by = None
