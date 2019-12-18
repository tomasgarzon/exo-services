# -*- coding: utf-8 -*-
import factory

from utils.faker_factory import faker


class TagFactory(factory.DictFactory):
    name = factory.Sequence(lambda x: faker.word() + str(faker.pyint()))
    tag = factory.Sequence(lambda x: faker.word())
    canonical = factory.Sequence(lambda x: faker.word())
