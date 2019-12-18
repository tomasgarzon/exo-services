from django.db import models
from model_utils.models import TimeStampedModel
from django.contrib.postgres.fields import JSONField

from ..conf import settings


def default_launch(*args, **kwargs):
    return {
        'send_welcome_consultant': False,
        'send_welcome_participant': False,
        'fix_password': ''
    }


class ProjectSettings(TimeStampedModel):
    project = models.OneToOneField(
        'Project', related_name='project_settings',
        on_delete=models.CASCADE)
    launch = JSONField(
        default=default_launch)
    participant_step_feedback_enabled = models.BooleanField(default=False)
    participant_step_microlearning_enabled = models.BooleanField(default=False)
    hide_from_my_jobs = models.BooleanField(default=False)
    team_communication = models.BooleanField(default=True)
    ask_to_ecosystem = models.BooleanField(default=True)
    directory = models.BooleanField(default=True)
    advisor_request = models.BooleanField(default=False)
    version = models.CharField(
        max_length=1,
        choices=settings.PROJECT_CH_VERSION,
        default=settings.PROJECT_CH_VERSION_DEFAULT)
    template_assignments = models.CharField(
        max_length=1,
        default='',
        null=True)

    def __str__(self):
        return str(self.project)
