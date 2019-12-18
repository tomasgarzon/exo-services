from singleton_decorator import singleton

from conversations.models import Conversation

from populate.populator.manager import Manager
from .conversations_builder import ConversationBuilder


@singleton
class ConversationsManager(Manager):
    model = Conversation
    attribute = 'uuid'
    builder = ConversationBuilder
    files_path = '/conversations/files/'
