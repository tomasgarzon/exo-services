from populate.populator.common.errors import ConfigurationError
from .consultant_manager import ConsultantManager


def consultant_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as consultant'.format(item))
    return ConsultantManager().get_object(item)
