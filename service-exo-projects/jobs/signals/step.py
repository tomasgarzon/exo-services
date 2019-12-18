from django.apps import apps

from ..models import Job

UserProjectRole = apps.get_model('project', 'UserProjectRole')


def post_save_step_handler(sender, instance, created, *args, **kwargs):
    for instance in UserProjectRole.objects.filter_by_project(instance.project):
        Job.objects.update_or_create(user_project_role=instance)
