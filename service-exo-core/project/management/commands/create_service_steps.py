from django.core.management.base import BaseCommand

from project.models import Project, Step


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('\n Found %s objects without steps: ' % Project.objects.filter(steps__isnull=True).count())  # NOQA
        for prj in Project.objects.filter(steps__isnull=True):
            Step.objects.create_steps(prj)
            if prj.start:
                Step.objects.start_steps(prj)

            if prj.steps.count():
                print('  Created steps for %s  ' % prj)     # NOQA

        print(' \n\n Done!! \n')    # NOQA
