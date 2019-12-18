import factory

from factory import django

from exo_hub.faker_factories import FakeExOHubFactory
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from ..models import HubUser


class FakeHubUserFactory(django.DjangoModelFactory):

    class Meta:
        model = HubUser

    user = factory.SubFactory(FakeUserFactory)
    hub = factory.SubFactory(FakeExOHubFactory)
