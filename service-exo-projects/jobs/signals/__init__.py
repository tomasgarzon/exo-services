from django.apps import apps
from django.db.models.signals import post_save, post_delete

from .user_project_role import (
    post_job_save_handler,
    post_job_delete_handler,
    change_user_role_handler)

from .job import create_job_handler
from .step import post_save_step_handler


def setup_signals():
    Job = apps.get_model('jobs', 'Job')
    Step = apps.get_model('project', 'Step')
    UserProjectRole = apps.get_model('project', 'UserProjectRole')
    UserTeamRole = apps.get_model('team', 'UserTeamRole')

    post_save.connect(post_job_save_handler, sender=Job)
    post_delete.connect(post_job_delete_handler, sender=Job)

    post_save.connect(create_job_handler, sender=UserProjectRole)
    post_save.connect(post_save_step_handler, sender=Step)
    post_save.connect(change_user_role_handler, sender=UserTeamRole)
    post_delete.connect(change_user_role_handler, sender=UserTeamRole)
