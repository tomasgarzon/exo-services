from django.apps import apps
from django.db.models.signals import post_save, post_delete

from .project import post_created_project, project_start_changed_handler
from .step import (
    post_save_step, step_started_changed_handler,
    create_feedback_for_each_step_stream_handler)
from .user_project_role  import (
    post_save_user_project_role,
    post_delete_user_project_role)
from .interaction_handler import post_save_overall_rating_team_step_handler

from ..signals_define import (
    project_created_signal,
    project_started_changed,
    step_started_changed)

from team.signals_define import signal_post_overall_rating_team_step_save

def setup_signals():

    Step = apps.get_model(app_label='project', model_name='Step')
    TeamStep = apps.get_model(app_label='team', model_name='TeamStep')
    StepStream = apps.get_model(app_label='project', model_name='StepStream')
    Project = apps.get_model(app_label='project', model_name='Project')
    UserProjectRole = apps.get_model(app_label='project', model_name='UserProjectRole')

    project_created_signal.connect(post_created_project)
    post_save.connect(post_save_step, sender=Step)
    post_save.connect(post_save_user_project_role, sender=UserProjectRole)
    post_delete.connect(post_delete_user_project_role, sender=UserProjectRole)
    project_started_changed.connect(
        project_start_changed_handler,
        sender=Project)
    step_started_changed.connect(
        step_started_changed_handler,
        sender=Step)
    signal_post_overall_rating_team_step_save.connect(
        post_save_overall_rating_team_step_handler,
        sender=TeamStep)

    post_save.connect(
        create_feedback_for_each_step_stream_handler,
        sender=StepStream)
