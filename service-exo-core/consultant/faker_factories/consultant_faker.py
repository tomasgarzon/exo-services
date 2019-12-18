import factory
from factory import django

from exo_activity.models import ExOActivity
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from utils.faker_factory import faker

from ..models import Consultant
from ..conf import settings


class FakeConsultantFactory(django.DjangoModelFactory):

    class Meta:
        model = Consultant

    user = factory.SubFactory(FakeUserFactory)
    primary_phone = factory.LazyAttribute(lambda x: faker.phone_number())
    secondary_phone = factory.LazyAttribute(lambda x: faker.phone_number())
    status = settings.CONSULTANT_STATUS_CH_ACTIVE

    @classmethod
    def create(cls, **kwargs):
        """Create an instance of the associated class, with overriden attrs."""
        activities = kwargs.pop('activities', [])
        marketplace_perm = kwargs.pop('marketplace_perm', True)

        instance = super().create(**kwargs)

        for activity_code in activities:
            exo_activity, _ = instance.exo_profile.exo_activities.get_or_create(
                exo_activity=ExOActivity.objects.get(code=activity_code))

        if marketplace_perm:
            instance.user.add_django_permission(settings.EXO_ACCOUNTS_PERMS_MARKETPLACE_FULL)

        return instance

    @factory.post_generation
    def languages(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for language in extracted:
                self.languages.add(language)
