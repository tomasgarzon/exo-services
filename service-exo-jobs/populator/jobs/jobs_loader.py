from populate.populator.common.errors import ConfigurationError
from .job_manager import JobManager


def job_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as a job'.format(item))
    return JobManager().get_object(item)
