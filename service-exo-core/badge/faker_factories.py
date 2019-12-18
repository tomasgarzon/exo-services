import factory

from factory import django, fuzzy

from utils.faker_factory import faker

from .models import Badge, UserBadge, UserBadgeItem
from .conf import settings


class FakeBadgeFactory(django.DjangoModelFactory):
    code = fuzzy.FuzzyChoice(dict(settings.BADGE_CODE_CHOICES).keys())

    class Meta:
        model = Badge


class FakeUserBadgeFactory(django.DjangoModelFactory):
    user = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
    badge = factory.SubFactory(FakeBadgeFactory)

    class Meta:
        model = UserBadge


class FakeUserBadgeItemFactory(django.DjangoModelFactory):
    user_badge = factory.SubFactory(FakeUserBadgeFactory)
    name = factory.LazyAttribute(lambda x: faker.word())
    date = factory.LazyAttribute(lambda x: faker.date())

    class Meta:
        model = UserBadgeItem
