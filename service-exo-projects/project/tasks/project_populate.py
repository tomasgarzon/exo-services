from django.apps import apps

from celery import Task


class ProjectPopulateTask(Task):
    name = 'ProjectPopulateTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Project = apps.get_model('project', 'Project')
        Step = apps.get_model('project', 'Step')
        project = Project.objects.get(pk=kwargs.get('project_id'))
        project.populate()
        if project.start:
            Step.objects.start_steps(project)
