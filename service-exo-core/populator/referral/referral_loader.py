from populate.populator.common.errors import ConfigurationError

from .referral_manager import ReferralManager


def referral_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as campaign'.format(item))
    return ReferralManager().get_object(item)
