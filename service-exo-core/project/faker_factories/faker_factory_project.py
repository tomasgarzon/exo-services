# -*- coding: utf-8 -*-
from factory import fuzzy, django  # noqa
import factory

from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from utils.faker_factory import faker
from utils.dates import string_to_timezone
from relation.faker_factories import (
    FakeConsultantProjectRoleFactory,
    FakePartnerProjectRoleFactory
)

from ..models import Project
from ..conf import settings


class FakeProjectFactory(django.DjangoModelFactory):

    class Meta:
        model = Project

    name = factory.LazyAttribute(lambda x: faker.word() + faker.numerify())
    customer = factory.SubFactory('customer.faker_factories.FakeCustomerFactory')
    start = factory.LazyAttribute(
        lambda x: faker.date_time(tzinfo=string_to_timezone('utc')),
    )
    duration = 3
    lapse = settings.PROJECT_LAPSE_WEEK
    agenda = factory.LazyAttribute(lambda x: faker.url())
    created_by = factory.SubFactory(FakeUserFactory)
    location = factory.LazyAttribute(lambda x: '{}, {}'.format(faker.city(), faker.country()))
    timezone = factory.LazyAttribute(lambda x: faker.timezone())

    @factory.post_generation
    def consultants(self, created, extracted, **kwargs):
        if not created:
            return None

        if extracted:
            for consultant in extracted:
                new_consultant = FakeConsultantProjectRoleFactory(
                    project=self,
                    consultant=consultant,
                )
                new_consultant.save()

    @factory.post_generation
    def partners(self, created, extracted, **kwargs):
        if not created:
            return None

        if extracted:
            for partner in extracted:
                new_partner = FakePartnerProjectRoleFactory(
                    project=self,
                    partner=partner,
                )
                new_partner.save()
