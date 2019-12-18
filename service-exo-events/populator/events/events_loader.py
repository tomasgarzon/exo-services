from populate.populator.common.errors import ConfigurationError
from .event_manager import EventManager


def event_constructor(loader, node):
    item = loader.construct_mapping(node=node)
    if not isinstance(item, dict) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as an event'.format(item))
    return EventManager().get_object(item)
