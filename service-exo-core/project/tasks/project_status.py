import logging

from celery import Task

from django.contrib.auth import get_user_model
from django.apps import apps

logger = logging.getLogger('service')


class StartProjectTask(Task):
    name = 'StartProjectTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Project = apps.get_model('project', 'Project')
        try:
            project = Project.objects.get(pk=kwargs.get('project_id'))
        except Project.DoesNotExist:
            return
        user_from = get_user_model().objects.get(pk=kwargs.get('user_from_id'))
        logging.info('Mark project {} as started'.format(project.name))
        if not project.is_finished:
            project.set_started(user_from, project.start)


class FinishProjectTask(Task):
    name = 'FinishProjectTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Project = apps.get_model('project', 'Project')
        try:
            project = Project.objects.get(pk=kwargs.get('project_id'))
        except Project.DoesNotExist:
            return
        user_from = get_user_model().objects.get(pk=kwargs.get('user_from_id'))
        logging.info('Mark project {} as finished'.format(project.name))
        project.set_finished(user_from, project.end)
