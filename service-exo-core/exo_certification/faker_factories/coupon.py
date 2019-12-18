import factory
import random

from factory import django

from utils.faker_factory import faker

from ..models import Coupon


class FakeCouponFactory(django.DjangoModelFactory):

    class Meta:
        model = Coupon

    code = factory.LazyAttribute(lambda x: faker.word())
    max_uses = random.randint(1, 21)
    discount = random.randint(1, 6) * 100
