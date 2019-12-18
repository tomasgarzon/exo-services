# -*- coding: utf-8 -*-
# Third Party Library
import factory

from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from customer.faker_factories import FakeCustomerFactory

from ..models import CustomerUserRole
from .faker_factory_role_factory import FactoryRoleFactory


class FakeCustomerUserRoleFactory(FactoryRoleFactory):

    class Meta:
        model = CustomerUserRole

    customer = factory.SubFactory(FakeCustomerFactory)
    user = factory.SubFactory(FakeUserFactory)
    position = factory.fuzzy.FuzzyChoice(
        ['CTO', 'CFO', 'Staff', 'CEO'],
    )
