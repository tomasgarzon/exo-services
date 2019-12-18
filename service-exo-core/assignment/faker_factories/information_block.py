import factory

from django.conf import settings

from factory import django, fuzzy

from utils.faker_factory import faker

from ..models import InformationBlock


class FakeInformationBlockFactory(django.DjangoModelFactory):

    class Meta:
        model = InformationBlock

    content_object = None
    title = factory.LazyAttribute(lambda x: faker.word())
    subtitle = factory.LazyAttribute(lambda x: faker.word())
    type = fuzzy.FuzzyChoice(
        dict(settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPES).keys(),
    )
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
