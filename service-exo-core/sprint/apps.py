from django.apps import AppConfig


class SprintConfig(AppConfig):
    name = 'sprint'
    verbose_name = 'Sprints'

    def ready(self):
        pass
