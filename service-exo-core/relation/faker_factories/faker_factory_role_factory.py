# -*- coding: utf-8 -*-
# Third Party Library
from factory import django
from factory import fuzzy

from ..models import Role
from ..conf import settings


class FactoryRoleFactory(django.DjangoModelFactory):

    class Meta:
        model = Role

    status = fuzzy.FuzzyChoice(
        dict(settings.RELATION_ROLE_CH_STATUS).keys()
    )
