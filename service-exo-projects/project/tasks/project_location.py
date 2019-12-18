from django.conf import settings
from django.apps import apps

from utils.dates import find_place_id, find_address

from celery import Task


class ProjectLocationTask(Task):
    name = 'ProjectLocationTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Project = apps.get_model('project', 'Project')
        project = Project.objects.get(pk=kwargs.get('project_id'))
        if settings.POPULATOR_MODE:
            return
        if project.location is None:
            return
        if project.place_id is None:
            place_id = find_place_id(project.location)
            if not place_id:
                return
            project.place_id = place_id
        location = find_address(project.place_id)
        if location is None:
            return
        project.location = location
        project.save()
