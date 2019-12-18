from singleton_decorator import singleton

from auth.models import User

from populate.populator.manager import Manager
from .auth_builder import UserBuilder


@singleton
class UserManager(Manager):
    model = User
    attribute = 'title'
    builder = UserBuilder
    files_path = '/auth/files/'
