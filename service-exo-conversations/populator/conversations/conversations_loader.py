from populate.populator.common.errors import ConfigurationError
from .conversations_manager import ConversationManager


def conversation_constructor(loader, node):
    item = loader.construct_mapping(node=node)
    if not isinstance(item, dict) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as an opportunity'.format(item))
    return ConversationManager().get_object(item)
