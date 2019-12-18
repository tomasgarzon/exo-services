from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from singleton_decorator import singleton

from populate.populator.manager import Manager
from .accounts_builder import AccountsBuilder


@singleton
class AccountsManager(Manager):

    model = get_user_model()
    attribute = 'uuid'
    builder = AccountsBuilder
    files_path = '/accounts/files/'

    def get_object(self, value):
        try:
            return super().get_object(value)
        except IntegrityError:
            data = self.load_file(value)
            obj = get_user_model().objects.filter(uuid=data['uuid']).get()
            obj.delete()
            obj = self.builder(data).create_object()
            self.output_success(obj, 'updated!')
            return obj
