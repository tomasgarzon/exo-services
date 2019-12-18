import logging

from django.core.management.base import BaseCommand

from ...models import UserProjectRole

logger = logging.getLogger('service')


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating jobs ...')

        for instance in UserProjectRole.objects.all():
            instance.save()

        self.stdout.write('Jobs created')
