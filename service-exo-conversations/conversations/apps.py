from django.apps import AppConfig


class ConversationsConfig(AppConfig):
    name = 'conversations'

    def ready(self):
        from actstream import registry
        from .signals import setup_signals
        setup_signals()
        registry.register(self.get_model('Conversation'))
        registry.register(self.get_model('Message'))
