from populate.populator.common.errors import ConfigurationError
from .payments_manager import PaymentManager


def payment_constructor(loader, node):
    item = loader.construct_mapping(node=node)
    if not isinstance(item, dict) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as an opportunity'.format(item))
    return PaymentManager().get_object(item)
