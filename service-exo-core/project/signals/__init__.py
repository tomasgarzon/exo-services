from django.apps import apps
from django.db.models.signals import post_save, pre_delete, pre_save

from forum.signals_define import signal_post_overall_rating_answer_save
from team.signals_define import signal_post_overall_rating_team_step_save

from .project import (
    post_save_service, update_start_date,
    update_duration,
    pre_delete_project,
    update_project_status,
    pre_save_project,
    create_external_info_handler,
)
from .step import (
    post_save_step,
    signal_create_feedback_for_each_step_stream)
from ..signals_define import (
    edit_project_start_date,
    edit_project_duration_date,
    project_status_signal,
    project_post_launch,
)
from .interaction_handler import (
    post_save_overall_rating_team_step_handler,
    post_save_overall_rating_answer_handler)


def setup_signals():

    Project = apps.get_model(
        app_label='project', model_name='Project',
    )
    Step = apps.get_model(
        app_label='project', model_name='Step',
    )
    StepStream = apps.get_model(
        app_label='project', model_name='StepStream',
    )
    Answer = apps.get_model(
        app_label='forum', model_name='Answer')
    TeamStep = apps.get_model(
        app_label='team', model_name='TeamStep')

    for subclass in Project.__subclasses__():
        pre_save.connect(pre_save_project, sender=subclass)
        post_save.connect(post_save_service, sender=subclass)
        project_post_launch.connect(create_external_info_handler, sender=subclass)
    post_save.connect(post_save_service, sender=Project)
    pre_save.connect(pre_save_project, sender=Project)
    post_save.connect(post_save_step, sender=Step)
    pre_delete.connect(pre_delete_project, sender=Project)

    edit_project_start_date.connect(update_start_date)
    edit_project_duration_date.connect(update_duration)

    project_status_signal.connect(update_project_status)
    project_post_launch.connect(create_external_info_handler, sender=Project)

    post_save.connect(
        signal_create_feedback_for_each_step_stream,
        sender=StepStream)

    signal_post_overall_rating_answer_save.connect(
        post_save_overall_rating_answer_handler,
        sender=Answer)

    signal_post_overall_rating_team_step_save.connect(
        post_save_overall_rating_team_step_handler,
        sender=TeamStep)
