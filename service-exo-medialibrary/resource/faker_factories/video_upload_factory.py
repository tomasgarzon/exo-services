# -*- coding: utf-8 -*-
import factory

from utils.faker_factory import faker

from ..conf import settings


class VideoUploadFactory(factory.DictFactory):
    url = factory.Sequence(lambda x: faker.url())
    name = factory.Sequence(lambda x: faker.word() + str(faker.pyint()))
    description = factory.Sequence(lambda x: faker.text())
    sections = [settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED]
    tags = []
