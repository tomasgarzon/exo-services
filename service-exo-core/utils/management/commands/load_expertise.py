from django.core.management.base import BaseCommand
from django.conf import settings

from keywords.models import Keyword


class Command(BaseCommand):
    help = 'Load expertise from txt'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('data', nargs='+', type=str)

    def create_expertise(self, value):
        keyword, _ = Keyword.objects.get_or_create(
            name=value,
            public=True,
        )
        keyword.tags.add(settings.KEYWORDS_CH_EXPERTISE)

    def handle(self, *args, **options):
        filename = options.get('data')[0]
        self.stdout.write('Creating expertise, reading text from "%s"...' % filename)

        with open(filename) as f:
            value = f.readline().replace('\n', '')
            while(value):
                self.create_expertise(value)
                value = f.readline().replace('\n', '')
        total = Keyword.objects.filter(tags__name=settings.KEYWORDS_CH_EXPERTISE).count()
        self.stdout.write(
            self.style.SUCCESS('Created "%s" expertises' % total),
        )
