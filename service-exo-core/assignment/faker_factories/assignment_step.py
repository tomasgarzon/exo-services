import factory

from django.conf import settings

from factory import django, fuzzy

from utils.faker_factory import faker

from ..models import AssignmentStep


class FakeAssignmentStepFactory(django.DjangoModelFactory):

    class Meta:
        model = AssignmentStep

    step = factory.SubFactory('project.faker_factories.FakeStepFactory')
    name = factory.LazyAttribute(lambda x: faker.word())
    streams = fuzzy.FuzzyChoice(
        dict(settings.PROJECT_STREAM_CH_TYPE).keys(),
    )
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
