from populate.populator.common.errors import ConfigurationError

from .exo_account_manager import ExoAccountManager


def exo_account_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as account'.format(item)
        )

    return ExoAccountManager().get_object(item)
