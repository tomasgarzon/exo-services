import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import Job


logger = logging.getLogger('service')


class Command(BaseCommand):
    help = (
        'Job Status'
    )

    def handle(self, *args, **options):
        self.stdout.write('Update Job Statuses')
        jobs = Job.objects.exclude(status=settings.JOBS_CH_STATUS_FINISHED)
        for job in jobs:
            job.set_status()
        self.stdout.write('Finish!!')
