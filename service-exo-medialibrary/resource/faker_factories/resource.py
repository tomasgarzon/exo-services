import factory

from factory import django, fuzzy  # noqa

from utils.faker_factory import faker  # noqa

from ..models import Resource
from ..conf import settings


class FakeResourceFactory(django.DjangoModelFactory):

    class Meta:
        model = Resource

    status = settings.RESOURCE_CH_STATUS_DRAFT
    type = settings.RESOURCE_CH_TYPE_VIDEO_VIMEO
    name = factory.Sequence(lambda x: faker.word())
    description = factory.Sequence(lambda x: faker.text())
    link = factory.Sequence(lambda x: 'https://vimeo.com/' + str(faker.pyint()))
    url = factory.Sequence(lambda x: faker.url())
    thumbnail = factory.Sequence(lambda x: faker.uri())
    duration = factory.Sequence(lambda x: faker.random_digit())
    sections = [settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED]
    projects = ''
    extra_data = ''
