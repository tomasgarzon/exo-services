from django.apps import AppConfig


class ForumConfig(AppConfig):
    name = 'forum'

    def ready(self):
        from .signals import setup_signals, setup_mentions
        from actstream import registry
        setup_signals()
        setup_mentions()
        registry.register(self.get_model('Post'))
        registry.register(self.get_model('Answer'))
        registry.register(self.get_model('Category'))
