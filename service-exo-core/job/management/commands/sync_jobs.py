from django.core.management.base import BaseCommand

from qa_session.models import QASession
from project.models import Project

from ...models import CoreJob


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating jobs ...')

        CoreJob.objects.all().delete()

        for project in Project.objects.all():
            project.update_related_jobs()

        for qa_session in QASession.objects.all():
            qa_session.update_related_jobs()

        self.stdout.write(self.style.SUCCESS('Jobs created'))
