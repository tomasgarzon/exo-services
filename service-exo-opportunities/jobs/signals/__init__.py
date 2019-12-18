from django.apps import apps
from django.db.models.signals import post_save, post_delete

from .applicant import post_job_save_handler, post_job_delete_handler
from .job import create_job_handler
from ..signals_define import create_job


def setup_signals():
    Job = apps.get_model('jobs', 'Job')

    post_save.connect(post_job_save_handler, sender=Job)
    post_delete.connect(post_job_delete_handler, sender=Job)

    create_job.connect(create_job_handler)
