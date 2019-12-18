# -*- coding: utf-8 -*-
import factory
from factory import fuzzy, django
from faker import Factory as FakerFactory

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.timezone import now

from ..models.mixins import UserProfileMixin
from ..models import SocialNetwork
from ..conf import settings

faker = FakerFactory.create(getattr(settings, 'FAKER_SETTINGS_LOCALE', 'en_GB'))

random_group = fuzzy.FuzzyChoice(Group.objects.all())


def fake_random_group():
    return random_group.fuzz()


class FakeUserProfileMixinFactory(django.DjangoModelFactory):

    class Meta:
        model = UserProfileMixin

    about_me = factory.LazyAttribute(lambda x: faker.text())
    bio_me = factory.LazyAttribute(lambda x: faker.text())
    short_me = factory.LazyAttribute(lambda x: faker.text())
    location = factory.LazyAttribute(lambda x: '{}, {}'.format(faker.city(), faker.country()))
    timezone = factory.LazyAttribute(lambda x: faker.timezone())


class FakeUserFactory(FakeUserProfileMixinFactory, django.DjangoModelFactory):
    """
        Creates a fake user.
    """

    class Meta:
        model = get_user_model()

    email = factory.LazyAttribute(lambda x: faker.email())
    short_name = factory.LazyAttribute(lambda x: faker.first_name())
    full_name = factory.LazyAttribute(lambda x: '{} {}'.format(faker.first_name(), faker.last_name()))
    password = factory.LazyAttribute(lambda o: o.short_name)
    last_login = now()
    is_active = True
    is_superuser = False
    is_staff = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        # The default would use ``manager.create(*args, **kwargs)``
        return manager.create_user(*args, **kwargs)


class FakeGroupFactory(django.DjangoModelFactory):
    name = factory.LazyAttribute(lambda x: faker.word())

    class Meta:
        model = Group


class FakeSocialNetworkFactory(django.DjangoModelFactory):

    """
        Creates a fake consultant.
    """

    class Meta:
        model = SocialNetwork

    user = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
    network_type = factory.fuzzy.FuzzyChoice(settings.EXO_ACCOUNTS_SOCIAL_TYPES)

    @factory.post_generation
    def value(self, create, extracted, **kwargs):
        network_type = self.network_type
        if network_type == settings.EXO_ACCOUNTS_SOCIAL_LINKEDIN:
            return faker.url()
        return faker.word()
