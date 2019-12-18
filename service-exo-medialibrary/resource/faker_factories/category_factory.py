# -*- coding: utf-8 -*-
import factory

from utils.faker_factory import faker


class SubCategory(factory.DictFactory):
    name = factory.Sequence(lambda x: faker.word())


class CategoryFactory(factory.DictFactory):
    name = factory.Sequence(lambda x: faker.word() + str(faker.pyint()))
    subcategories = SubCategory.create_batch(size=4)
