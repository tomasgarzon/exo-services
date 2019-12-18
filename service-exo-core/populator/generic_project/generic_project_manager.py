from singleton_decorator import singleton

from generic_project.models import GenericProject

from populate.populator.manager import Manager
from .generic_project_builder import GenericProjectBuilder


@singleton
class GenericProjectManager(Manager):

    model = GenericProject
    attribute = 'name'
    builder = GenericProjectBuilder
    files_path = '/generic_project/files/'
