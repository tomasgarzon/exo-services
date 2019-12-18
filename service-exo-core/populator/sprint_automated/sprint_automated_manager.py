from singleton_decorator import singleton

from sprint_automated.models import SprintAutomated

from populate.populator.manager import Manager
from .sprint_automated_builder import SprintAutomatedBuilder


@singleton
class SprintAutomatedManager(Manager):

    model = SprintAutomated
    attribute = 'name'
    builder = SprintAutomatedBuilder
    files_path = '/sprint_automated/files/'
