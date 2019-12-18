from singleton_decorator import singleton

from relation.models import ConsultantRoleCertificationGroup

from populate.populator.manager import Manager
from .certification_builder import CertificationBuilder


@singleton
class CertificationManager(Manager):
    model = ConsultantRoleCertificationGroup
    attribute = 'name'
    builder = CertificationBuilder
    files_path = '/certification/files/'
