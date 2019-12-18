from singleton_decorator import singleton

from exo_certification.models import CertificationCohort

from populate.populator.manager import Manager
from .certification_cohort_builder import CertificationCohortBuilder


@singleton
class CertificationCohortManager(Manager):
    model = CertificationCohort
    attribute = 'uuid'
    builder = CertificationCohortBuilder
    files_path = '/certification_cohort/files/'
