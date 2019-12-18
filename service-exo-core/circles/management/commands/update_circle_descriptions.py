from django.conf import settings
from django.core.management import BaseCommand

from ...models import Circle


class Command(BaseCommand):

    help = (
        'Update platform owned circle descriptions'
    )

    def handle(self, *args, **options):
        for slug, description in settings.CIRCLES_CIRCLE_DESCRIPTIONS:
            try:
                circle = Circle.objects.get(slug=slug)
                circle.description = description
                circle.save()
                print('Updated {} circle'.format(circle.name))
            except Circle.DoesNotExist:
                print('Couldn\'t find {} circle, skipping!'.format(circle.name))
