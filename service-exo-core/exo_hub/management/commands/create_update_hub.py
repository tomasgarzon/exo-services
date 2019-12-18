from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import ExOHub


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating ExO Hubs ...'))

        order = 1

        for _type, name in settings.EXO_HUB_CH_EXO_TYPE:

            ExOHub.objects.update_or_create(
                _type=_type,
                defaults={
                    'name': name,
                    'order': order,
                }
            )
            order += 1

        self.stdout.write(
            self.style.SUCCESS('Created "{}" ExO Hubs').format(ExOHub.objects.count())
        )
