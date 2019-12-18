from singleton_decorator import singleton

from landing.models import Page

from populate.populator.manager import Manager
from .landing_builder import LandingBuilder


@singleton
class LandingManager(Manager):
    model = Page
    attribute = 'uuid'
    builder = LandingBuilder
    files_path = '/landing/files/'
