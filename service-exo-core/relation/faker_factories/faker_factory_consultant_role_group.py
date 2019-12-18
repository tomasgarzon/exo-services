# -*- coding: utf-8 -*-
import factory

from factory import django

from utils.faker_factory import faker

from ..models import ConsultantRoleCertificationGroup
from ..conf import settings


class FakeConsultantRoleGroupFactory(django.DjangoModelFactory):

    class Meta:
        model = ConsultantRoleCertificationGroup

    name = factory.LazyAttribute(lambda x: faker.name())
    description = factory.LazyAttribute(lambda x: faker.text())
    _type = factory.fuzzy.FuzzyChoice(dict(settings.RELATION_CONSULTANT_ROLE_GROUP_TYPE_CHOICES).keys())
