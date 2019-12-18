# -*- coding: utf-8 -*-
import factory
import pytz

from utils.faker_factory import faker

from ..conf import settings


class VideoFactory(factory.DictFactory):
    type = settings.RESOURCE_CH_TYPE_VIDEO_VIMEO
    status = settings.RESOURCE_PROVIDER_STATUS_AVAILABLE
    name = factory.Sequence(lambda x: faker.word() + str(faker.pyint()))
    description = factory.Sequence(lambda x: faker.text())
    link = factory.Sequence(lambda x: 'https://vimeo.com/' + str(faker.pyint()))
    url = factory.Sequence(lambda x: faker.url())
    sections = [settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED]
    thumbnail = factory.Sequence(lambda x: faker.url())
    duration = factory.Sequence(lambda x: faker.random_digit())
    modified = factory.Sequence(lambda x: faker.date_time_this_year(
        before_now=True,
        tzinfo=pytz.timezone('utc')).isoformat())
    pictures = {
        "sizes": [{
            "link": "https://i.vimeocdn.com/video/686815740_100x75.jpg?r=pad",
        }, {
            "link": "https://i.vimeocdn.com/video/686815740_200x150.jpg?r=pad",
        }, {
            "link": "https://i.vimeocdn.com/video/686815740_295x166.jpg?r=pad",
        }]
    }
