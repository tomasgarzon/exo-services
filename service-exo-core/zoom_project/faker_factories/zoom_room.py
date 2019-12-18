# -*- coding: utf-8 -*-
import factory
from factory import django  # noqa
from django.contrib.contenttypes.models import ContentType

from utils.faker_factory import faker

from ..models import ZoomRoom


class FakeZoomRoomFactory(django.DjangoModelFactory):

    _zoom_settings = factory.SubFactory(
        'zoom_project.faker_factories.FakeZoomSettingsFactory',
    )

    meeting_id = factory.LazyAttribute(lambda x: faker.word())
    host_meeting_id = factory.LazyAttribute(lambda x: faker.word())

    object_id = factory.SelfAttribute('content_object.id')
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object),
    )

    class Meta:
        exclude = ['content_object']
        abstract = True


class FakeZoomRoomTeamFactory(FakeZoomRoomFactory):

    content_object = factory.SubFactory('team.faker_factories.FakeTeamFactory')

    class Meta:
        model = ZoomRoom
