import factory
import factory.fuzzy

from django.conf import settings

from utils.faker_factory import faker
from exo_role.models import ExORole

from ..models import OpportunityGroup


class FakeOpportunityGroupFactory(factory.django.DjangoModelFactory):
    total = 1
    entity = factory.LazyAttribute(lambda x: faker.company())
    origin = 'T'
    duration_unity = factory.fuzzy.FuzzyChoice(
        dict(settings.OPPORTUNITIES_DURATION_UNITY_CHOICES).keys(),
    )
    duration_value = faker.random_digit_not_null()
    exo_role = factory.Iterator(ExORole.objects.all())

    class Meta:
        model = OpportunityGroup
