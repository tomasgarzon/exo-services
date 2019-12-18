import factory

from django.conf import settings

from factory import django

from custom_auth.faker_factories import FakeInternalOrganizationFactory
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from utils.faker_factory import faker

from ..models import OrganizationUserRole


class FakeInternalOrganizationUserRoleFactory(django.DjangoModelFactory):

    class Meta:
        model = OrganizationUserRole

    organization = factory.SubFactory(FakeInternalOrganizationFactory)
    user = factory.SubFactory(FakeUserFactory)
    position = factory.LazyAttribute(lambda x: faker.name())
    status = settings.RELATION_ROLE_CH_ACTIVE
