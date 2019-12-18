# -*- coding: utf-8 -*-
# Third Party Library
import factory
from django.conf import settings

from exo_role.models import ExORole

from ..models import UserProjectRole
from .faker_factory_role_factory import FactoryRoleFactory


class FakeUserProjectRoleFactory(FactoryRoleFactory):

    class Meta:
        model = UserProjectRole

    project = factory.SubFactory('project.faker_factories.FakeProjectFactory')
    user = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
    exo_role = factory.LazyAttribute(lambda o: ExORole.objects.get(
        code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT))

    @classmethod
    def create(cls, **kwargs):
        role_code = kwargs.pop('exo_role', None)

        if role_code:
            kwargs['exo_role'] = ExORole.objects.get(code=role_code)

        instance = super().create(**kwargs)

        return instance
