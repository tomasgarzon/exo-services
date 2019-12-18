# -*- coding: utf-8 -*-
# Third Party Library
import factory
from factory import django

# Project Library
from utils.faker_factory import faker

from .models import Partner


class FakePartnerFactory(django.DjangoModelFactory):

    class Meta:
        model = Partner

    name = factory.LazyAttribute(lambda x: faker.name())
