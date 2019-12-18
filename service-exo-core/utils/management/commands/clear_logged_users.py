from importlib import import_module

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Clear logged users'

    def handle(self, *args, **options):
        engine = import_module(settings.SESSION_ENGINE)
        engine.SessionStore.get_model_class().objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS('Sessions removed'),
        )
