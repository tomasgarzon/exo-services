from django.apps import AppConfig


class AchievementConfig(AppConfig):
    name = 'achievement'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
