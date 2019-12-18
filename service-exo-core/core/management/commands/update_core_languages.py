import os

from django.core.management.base import BaseCommand
from django.conf import settings

from .load_languages import Command as LoadLanguagesCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        LANGUAGES_FILE = os.path.join(settings.BASE_DIR, 'data/languages.txt')
        lng_loader = LoadLanguagesCommand()

        with open(LANGUAGES_FILE) as f:
            values = f.readlines()
            lng_loader.create_languages(values)
