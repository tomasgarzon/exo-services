from singleton_decorator import singleton

from consultant.models import Consultant

from populate.populator.manager import Manager
from .consultant_builder import ConsultantBuilder


@singleton
class ConsultantManager(Manager):
    model = Consultant
    attribute = 'user__full_name'
    builder = ConsultantBuilder
    files_path = '/consultant/files/'
    manager = 'all_objects'

    def output_success(self, object, msg):
        self.cmd.stdout.write(
            self.cmd.style.SUCCESS(
                self.model.__name__ + ' ' + getattr(
                    object.user, 'full_name') + ' ' + msg))
