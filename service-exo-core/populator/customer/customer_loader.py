from populate.populator.common.errors import ConfigurationError
from .customer_manager import CustomerManager


def customer_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as customer'.format(item))
    return CustomerManager().get_object(item)
