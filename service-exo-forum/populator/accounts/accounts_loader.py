from populate.populator.common.errors import ConfigurationError
from .accounts_manager import AccountsManager


def account_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as account'.format(item))
    return AccountsManager().get_object(item)
