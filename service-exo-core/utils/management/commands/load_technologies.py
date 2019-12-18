import json

from django.core.management.base import BaseCommand
from django.conf import settings

from keywords.models import Keyword


class Command(BaseCommand):
    help = 'Load Technologies from json'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('data', nargs='+', type=str)

    def create_technology(self, value):
        keyword, _ = Keyword.objects.get_or_create(
            name=value.get('title'),
            public=True,
        )
        keyword.tags.add(settings.KEYWORDS_CH_TECHNOLOGY)

    def handle(self, *args, **options):
        filename = options.get('data')[0]
        self.stdout.write('Creating technologies, reading JSON from "%s"...' % filename)

        with open(filename) as f:
            values = f.read()
            technologies = json.loads(values)
            for value in technologies:
                self.create_technology(value)
        total = Keyword.objects.filter(tags__name=settings.KEYWORDS_CH_TECHNOLOGY).count()
        self.stdout.write(
            self.style.SUCCESS('Created "%s" technologies' % total),
        )
