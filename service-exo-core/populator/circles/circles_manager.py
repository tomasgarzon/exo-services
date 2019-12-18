from singleton_decorator import singleton

from circles.models import Circle

from populate.populator.manager import Manager
from .circles_builder import CirclesBuilder


@singleton
class CirclesManager(Manager):
    model = Circle
    attribute = 'name'
    builder = CirclesBuilder
    files_path = '/circles/files/'
