import factory

from factory import django

from exo_accounts.test_mixins import FakeUserFactory
from utils.faker_factory import faker

from ..models import CertificationRequest
from .coupon import FakeCouponFactory


class FakeCertificationRequestFactory(django.DjangoModelFactory):

    class Meta:
        model = CertificationRequest

    user = factory.SubFactory(FakeUserFactory)
    payment_uuid = factory.LazyAttribute(lambda x: faker.uuid4())
    payment_url = factory.LazyAttribute(lambda x: faker.uri())
    coupon = factory.SubFactory(FakeCouponFactory)
    price = factory.LazyAttribute(lambda x: faker.numerify())
