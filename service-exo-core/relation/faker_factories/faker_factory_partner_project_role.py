# -*- coding: utf-8 -*-
# Third Party Library
import factory

from ..models import PartnerProjectRole
from .faker_factory_role_factory import FactoryRoleFactory


class FakePartnerProjectRoleFactory(FactoryRoleFactory):

    class Meta:
        model = PartnerProjectRole

    project = factory.SubFactory('project.faker_factories.FakeProjectFactory')
    partner = factory.SubFactory('partner.faker_factories.FakePartnerFactory')
