from singleton_decorator import singleton

from event.models import Event

from populate.populator.manager import Manager
from .events_builder import EventsBuilder


@singleton
class EventsManager(Manager):
    model = Event
    attribute = 'title'
    builder = EventsBuilder
    files_path = '/events/files/'
