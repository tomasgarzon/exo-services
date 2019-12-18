# -*- coding: utf-8 -*-
from factory import fuzzy, django  # noqa
import factory
import pytz

from utils.faker_factory import faker

from .models import QASession


class FakeQASessionFactory(django.DjangoModelFactory):

    class Meta:
        model = QASession

    project = factory.SubFactory('project.faker_factories.FakeProjectFactory')
    created_by = factory.SubFactory(
        'exo_accounts.test_mixins.faker_factories.FakeUserFactory')
    start_at = faker.date_time(tzinfo=pytz.UTC)
    end_at = faker.date_time(tzinfo=pytz.UTC)
