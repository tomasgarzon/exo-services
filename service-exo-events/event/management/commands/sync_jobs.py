from django.core.management.base import BaseCommand
from django.conf import settings

from jobs.models import Job

from ...models import Participant


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating Jobs for participants in events ...'))

        for participant in Participant.objects.all().filter_by_status(settings.EVENT_CH_ROLE_STATUS_ACTIVE):
            Job.objects.update_or_create(participant=participant)

        self.stdout.write(self.style.SUCCESS('{} jobs created').format(Job.objects.count()))
