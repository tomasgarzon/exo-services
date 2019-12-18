import factory

from django.db.models.signals import post_save

from factory import django

from utils.faker_factory import faker

from ..models import Payment
from ..conf import settings


@factory.django.mute_signals(post_save)
class FakePaymentFactory(django.DjangoModelFactory):

    class Meta:
        model = Payment

    intent_id = factory.LazyAttribute(lambda x: faker.ean())
    intent_client_secret_id = factory.LazyAttribute(lambda x: faker.ean())
    _type = factory.LazyAttribute(lambda x: settings.PAYMENTS_TYPE_CERTIFICATION)

    status = settings.PAYMENTS_CH_PENDING

    amount = factory.LazyAttribute(lambda x: faker.numerify())
    concept = factory.LazyAttribute(lambda x: faker.sentence())
    email = factory.LazyAttribute(lambda x: faker.email())
    full_name = factory.LazyAttribute(lambda x: faker.name())
    tax_id = factory.LazyAttribute(lambda x: faker.word())
    address = factory.LazyAttribute(lambda x: faker.sentence())
