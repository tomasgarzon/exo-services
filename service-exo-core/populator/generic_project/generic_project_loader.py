from populate.populator.common.errors import ConfigurationError
from .generic_project_manager import GenericProjectManager


def generic_project_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as generic project'.format(item))
    return GenericProjectManager().get_object(item)
