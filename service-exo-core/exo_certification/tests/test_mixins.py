from django.conf import settings

from ..models import CertificationCohort, ExOCertification
from utils.dates import string_to_datetime

from utils.faker_factory import faker


class ExOCertificationTestMixin:

    def create_cohorts(self):

        self.cohort_lvl_2 = CertificationCohort.objects.create(
            date=string_to_datetime(faker.date()),
            certification=ExOCertification.objects.get(
                level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2
            ),
            seats=25,
            price=1500,
            status=settings.EXO_CERTIFICATION_COHORT_STATUS_CH_OPEN,
            invoice_concept=' '.join(faker.words()),
        )
        self.cohort_lvl_2_ft = CertificationCohort.objects.create(
            date=string_to_datetime(faker.date()),
            certification=ExOCertification.objects.get(
                level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2A
            ),
            seats=25,
            price=1500,
            status=settings.EXO_CERTIFICATION_COHORT_STATUS_CH_OPEN,
            invoice_concept=' '.join(faker.words()),
        )
        self.cohort_lvl_3 = CertificationCohort.objects.create(
            date=string_to_datetime(faker.date()),
            certification=ExOCertification.objects.get(
                level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3
            ),
            seats=25,
            price=2500,
            first_price_tier=1250,
            status=settings.EXO_CERTIFICATION_COHORT_STATUS_CH_OPEN,
            invoice_concept=' '.join(faker.words()),
        )

    def create_cohort(self, level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2):
        certification = ExOCertification.objects.get(level=level)
        return CertificationCohort.objects.create(
            date=string_to_datetime(faker.date()),
            certification=certification,
            seats=25,
            price=2500,
            status=settings.EXO_CERTIFICATION_COHORT_STATUS_CH_OPEN,
            invoice_concept=' '.join(faker.words()),
        )
