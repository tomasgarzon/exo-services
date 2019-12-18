from django.core.management.base import BaseCommand

from utils.dates import iso_to_gregorian
from project.models import Project


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('\n Found %s objects without end date for step: ' % Project.objects.filter(steps__end__isnull=True).count())  # NOQA

        for prj in Project.objects.filter(steps__end__isnull=True):
            if prj.is_workshop:
                if prj.steps.first().start:
                    for step in prj.steps.all():
                        step.end = step.start
                        step.save()

                    print('  Updated WORKSHOP %s  ' % prj)     # NOQA

            elif prj.is_sprint:
                if prj.steps.first().start:
                    for step in prj.steps.all():
                        step.end = iso_to_gregorian(
                            step.start.isocalendar()[0],
                            step.start.isocalendar()[1],
                            5,
                        )
                        step.save()

                    print('  Updated SPRINT %s  ' % prj)     # NOQA

        print(' \n\n Done!! \n')    # NOQA
