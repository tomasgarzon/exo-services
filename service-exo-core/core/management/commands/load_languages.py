from django.core.management.base import BaseCommand
from core.models import Language


class Command(BaseCommand):
    help = 'Load Languages'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('data', nargs='+', type=str)

    def create_languages(self, values):
        for v in values:
            languages = v.replace('\n', '').replace(', ', ',').split(',')
            for name in languages:
                language, _ = Language.objects.get_or_create(name=name)

    def handle(self, *args, **options):
        print('Loading languages')  # noqa
        filename = options.get('data')[0]
        with open(filename) as f:
            values = f.readlines()
            self.create_languages(values)

        print(Language.objects.all())  # NOQA
