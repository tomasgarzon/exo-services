from populate.populator.common.errors import ConfigurationError
from .qa_session_manager import QaSessionManager


def qa_session_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted QA Session'.format(item))
    return QaSessionManager().get_object(item)
