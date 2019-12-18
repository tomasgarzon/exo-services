# -*- coding: utf-8 -*-
# Third Party Library
import factory

from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from partner.faker_factories import FakePartnerFactory

from ..models import PartnerUserRole
from .faker_factory_role_factory import FactoryRoleFactory


class FakePartnerUserRoleFactory(FactoryRoleFactory):

    class Meta:
        model = PartnerUserRole

    partner = factory.SubFactory(FakePartnerFactory)
    user = factory.SubFactory(FakeUserFactory)
    position = factory.fuzzy.FuzzyChoice(
        ['CTO', 'CFO', 'Staff', 'CEO'],
    )
