from populate.populator.common.errors import ConfigurationError
from .certification_cohort_manager import CertificationCohortManager


def certification_cohort_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as certification cohort'.format(item))
    return CertificationCohortManager().get_object(item)
