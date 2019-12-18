from populate.populator.common.errors import ConfigurationError
from .circles_manager import CirclesManager


def circle_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as circle'.format(item))
    return CirclesManager().get_object(item)
