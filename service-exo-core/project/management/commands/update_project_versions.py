from django.core.management.base import BaseCommand

from project.models import Project

from ...conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        for prj in Project.objects.all():
            if not prj.is_sprintautomated and not prj.is_genericproject:
                sett = prj.settings
                sett.version = settings.PROJECT_CH_VERSION_1
                sett.save()
