from django.core.management import BaseCommand
from django.conf import settings

from ...models import Circle

import os
import yaml


class Command(BaseCommand):
    FIXTURE_NAME = 'circles/fixtures/circles.yaml'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating circles ...'))
        filename = os.path.join(settings.BASE_DIR, self.FIXTURE_NAME)
        with open(filename, 'r') as f:
            data = yaml.load(f, Loader=yaml.Loader)
            for model in data:
                fields = model.get('fields')
                slug = fields.pop('slug')
                Circle.objects.get_or_create(
                    slug=slug,
                    defaults=fields)

        self.stdout.write(self.style.SUCCESS('Circles created'))
