# -*- coding: utf-8 -*-
from factory import django  # noqa

from ..models import ZoomSettings


class FakeZoomSettingsFactory(django.DjangoModelFactory):

    class Meta:
        model = ZoomSettings
