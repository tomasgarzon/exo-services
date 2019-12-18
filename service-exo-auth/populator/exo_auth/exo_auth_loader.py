from populate.populator.common.errors import ConfigurationError
from .auth_manager import UserManager


def user_constructor(loader, node):
    item = loader.construct_mapping(node=node)
    if not isinstance(item, dict) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as an opportunity'.format(item))
    return UserManager().get_object(item)
