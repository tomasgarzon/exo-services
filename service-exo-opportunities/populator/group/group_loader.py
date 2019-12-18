from populate.populator.common.errors import ConfigurationError
from .group_manager import GroupManager


def group_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as an opportunity group'.format(item))
    return GroupManager().get_object(item)
