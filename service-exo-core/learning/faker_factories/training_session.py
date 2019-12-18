# Third Party Library
import factory
import datetime
from factory import django

from utils.faker_factory import faker

from ..models import TrainingSession


class FakeTrainingSessionFactory(django.DjangoModelFactory):

    """
        Creates a fake consultant.
    """

    class Meta:
        model = TrainingSession

    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
    name = factory.LazyAttribute(lambda x: faker.text(max_nb_chars=20))
    description = factory.LazyAttribute(lambda x: faker.text())
    date = factory.fuzzy.FuzzyDate(datetime.date(2016, 1, 1))
