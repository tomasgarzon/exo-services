import factory

from datetime import datetime
from factory import django

from ..models import CertificationCohort


class FakeCertificationCohortFactory(django.DjangoModelFactory):

    class Meta:
        model = CertificationCohort

    date = factory.LazyAttribute(lambda x: datetime.now().date())
