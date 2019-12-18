import factory
from factory import django, fuzzy

from utils.faker_factory import faker

from ..conf import settings
from ..models import Agreement


class FakeAgreementFactory(django.DjangoModelFactory):

    class Meta:
        model = Agreement

    name = factory.LazyAttribute(lambda x: faker.sentence())
    description = factory.LazyAttribute(lambda x: faker.sentence())
    file_name = 'consultant_v3.html'
    recipient = fuzzy.FuzzyChoice(
        [x[0] for x in settings.AGREEMENT_RECIPIENT],
    )
    status = fuzzy.FuzzyChoice(
        [x[0] for x in settings.AGREEMENT_STATUS],
    )
    version = factory.LazyAttribute(
        lambda x: '{}.{}.{}'.format(
            faker.random_digit(),
            faker.random_digit(),
            faker.random_digit(),
        ),
    )

    domain = settings.AGREEMENT_DOMAIN_DEFAULT
