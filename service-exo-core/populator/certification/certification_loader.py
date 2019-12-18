from populate.populator.common.errors import ConfigurationError
from .certification_manager import CertificationManager


def certification_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as certification'.format(item))
    return CertificationManager().get_object(item)
