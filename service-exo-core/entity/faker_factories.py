# -*- coding: utf-8 -*-
import factory
from factory import fuzzy  # noqa

from utils.faker_factory import faker
from industry import models

from .conf import settings


class FakeEntityFactoryMixin(factory.Factory):

    name = factory.LazyAttribute(lambda x: faker.text(max_nb_chars=20))
    size = factory.fuzzy.FuzzyChoice(
        dict(settings.ENTITY_CH_ORGANIZATION_SIZE).keys()
    )
    annual_revenue = factory.fuzzy.FuzzyInteger(100, 2000)
    market_value = factory.fuzzy.FuzzyInteger(100, 2000)
    industry = factory.Iterator(models.Industry.objects.all())

    class Meta:
        abstract = True


class FakeContactFactoryMixin(factory.Factory):
    phone = factory.LazyAttribute(lambda x: faker.phone_number())
    website = factory.LazyAttribute(lambda x: faker.url())
    address = factory.LazyAttribute(lambda x: faker.address())
    postcode = factory.LazyAttribute(lambda x: faker.postcode())
    contact_person = factory.LazyAttribute(lambda x: '{},\n{},\n{}'.format(
        faker.name(), faker.company_email(), faker.phone_number(),
    ))
