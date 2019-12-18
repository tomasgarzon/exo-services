from django.apps import apps

from ..signals_define import (
    signal_conversation_group_created,
    signal_message_created,
    signal_message_seen)

from .notifications import (
    new_conversation_group_handler,
    new_message_handler,
    see_message_handler)
from .webhook import (
    new_message_opportunity_handler,
)


def setup_signals():
    Conversation = apps.get_model('conversations', 'Conversation')
    Message = apps.get_model('conversations', 'Message')

    signal_conversation_group_created.connect(
        new_conversation_group_handler,
        sender=Conversation)

    signal_message_created.connect(
        new_message_handler,
        sender=Message)

    signal_message_seen.connect(
        see_message_handler,
        sender=Message)

    signal_message_created.connect(
        new_message_opportunity_handler,
        sender=Message)
