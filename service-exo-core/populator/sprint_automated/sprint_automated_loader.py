from populate.populator.common.errors import ConfigurationError
from .sprint_automated_manager import SprintAutomatedManager


def sprint_automated_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as consultant'.format(item))
    return SprintAutomatedManager().get_object(item)
