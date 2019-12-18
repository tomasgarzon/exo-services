# -*- coding: utf-8 -*-
import factory

from django.conf import settings

from exo_role.models import ExORole

from ..models import ConsultantProjectRole
from .faker_factory_role_factory import FactoryRoleFactory


class FakeConsultantProjectRoleFactory(FactoryRoleFactory):

    class Meta:
        model = ConsultantProjectRole

    exo_role = factory.LazyAttribute(lambda o: ExORole.objects.get(
        code=settings.EXO_ROLE_CODE_SPRINT_COACH))
    project = factory.SubFactory('project.faker_factories.FakeProjectFactory')
    consultant = factory.SubFactory('consultant.faker_factories.FakeConsultantFactory')
