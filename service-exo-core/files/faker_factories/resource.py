# -*- coding: utf-8 -*-
import factory
from factory import django

from utils.faker_factory import faker

from ..models import Resource


class FakeResourceFileFactory(django.DjangoModelFactory):

    class Meta:
        model = Resource

    name = factory.LazyAttribute(lambda x: faker.word())
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
    extension = factory.LazyAttribute(lambda x: faker.file_extension())
    mimetype = factory.LazyAttribute(lambda x: faker.mime_type())
    _filename = factory.LazyAttribute(lambda x: faker.word())


class FakeResourceLinkFactory(django.DjangoModelFactory):

    class Meta:
        model = Resource

    name = factory.LazyAttribute(lambda x: faker.word())
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
    link = factory.LazyAttribute(lambda x: faker.uri())
