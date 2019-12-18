import factory
from factory import django

from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from .agreement_faker import FakeAgreementFactory
from ..conf import settings
from ..models import UserAgreement


class FakeUserAgreementFactory(django.DjangoModelFactory):

    class Meta:
        model = UserAgreement

    user = factory.SubFactory(FakeUserFactory)
    agreement = factory.SubFactory(FakeAgreementFactory)
    status = factory.fuzzy.FuzzyChoice(
        [x[0] for x in settings.AGREEMENT_USER_STATUS],
    )
