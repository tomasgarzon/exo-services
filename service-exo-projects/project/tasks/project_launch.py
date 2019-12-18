from django.apps import apps
from django.contrib.auth import get_user_model

from celery import Task


class ProjectLaunchTask(Task):
    name = 'ProjectLaunchTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Project = apps.get_model('project', 'Project')
        project = Project.objects.get(pk=kwargs.get('project_id'))
        user_from = get_user_model().objects.get(pk=kwargs.get('user_id'))
        message = kwargs.get('message')
        project.launch(user_from, message=message)
