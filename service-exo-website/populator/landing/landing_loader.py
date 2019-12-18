from populate.populator.common.errors import ConfigurationError
from .landing_manager import LandingManager


def landing_constructor(loader, node):
    item = loader.construct_mapping(node=node)
    if not isinstance(item, dict) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as a page'.format(item))
    return LandingManager().get_object(item)
