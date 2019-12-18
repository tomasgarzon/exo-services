from populate.populator.common.errors import ConfigurationError
from .opportunities_manager import OpportunitiesManager


def opportunity_constructor(loader, node):
    item = loader.construct_mapping(node=node)
    if not isinstance(item, dict) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as an opportunity'.format(item))
    return OpportunitiesManager().get_object(item)
