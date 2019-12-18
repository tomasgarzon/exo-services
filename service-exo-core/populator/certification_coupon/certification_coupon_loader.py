from populate.populator.common.errors import ConfigurationError
from .certification_coupon_manager import CertificationCouponManager


def certification_coupon_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as certification coupon'.format(item))
    return CertificationCouponManager().get_object(item)
