from django.apps import apps
from django.db.models.signals import post_save, post_delete

from .signal_handlers import (
    related_instance_post_update,
    related_instance_post_delete,
    job_instance_post_save,
    job_instance_post_delete,
    core_job_post_save,
    core_job_post_delete,
)
from ..models import CoreJob


def setup_signals():
    Project = apps.get_model(app_label='project', model_name='Project')
    QASession = apps.get_model(app_label='qa_session', model_name='QASession')

    ConsultantProjectRole = apps.get_model(app_label='relation', model_name='ConsultantProjectRole')
    UserProjectRole = apps.get_model(app_label='relation', model_name='UserProjectRole')
    QASessionAdvisor = apps.get_model(app_label='qa_session', model_name='QASessionAdvisor')

    job_instance_parent_models = [
        Project,
        QASession,
    ]

    job_instance_models = [
        ConsultantProjectRole,
        UserProjectRole,
        QASessionAdvisor,
    ]

    for model in job_instance_parent_models:
        post_save.connect(related_instance_post_update, sender=model)
        post_delete.connect(related_instance_post_delete, sender=model)

    for model in job_instance_models:
        post_save.connect(job_instance_post_save, sender=model)
        post_delete.connect(job_instance_post_delete, sender=model)

    # CoreJob signals
    post_save.connect(core_job_post_save, sender=CoreJob)
    post_delete.connect(core_job_post_delete, sender=CoreJob)
