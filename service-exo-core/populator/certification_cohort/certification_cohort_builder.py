from django.conf import settings

from populate.populator.builder import Builder
from populate.populator.common.helpers import find_tuple_values

from exo_certification.models import CertificationCohort, ExOCertification


class CertificationCohortBuilder(Builder):

    def create_object(self):
        status = find_tuple_values(
            settings.EXO_CERTIFICATION_COHORT_STATUS_CH_STATUSES,
            self.data.get('status'))[0]
        lang = find_tuple_values(
            settings.EXO_CERTIFICATION_COHORT_CH_LANGS,
            self.data.get('language'))[0]
        certification = ExOCertification.objects.get(
            level=self.data.get('certification')
        )

        return CertificationCohort.objects.create(
            certification=certification,
            uuid=self.data.get('uuid'),
            date=self.data.get('date'),
            seats=self.data.get('seats', 0),
            price=self.data.get('price'),
            currency=self.data.get('currency'),
            invoice_concept=self.data.get('invoice_concept'),
            language=lang,
            status=status,
        )
