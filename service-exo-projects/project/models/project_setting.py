from django.db import models
from django.contrib.postgres.fields import JSONField

from model_utils.models import TimeStampedModel


def default_launch_dict():
    return {
        'send_welcome_consultant': False,
        'send_welcome_participant': False,
        'default_password': ''
    }


class ProjectSettings(TimeStampedModel):
    project = models.OneToOneField(
        'Project',
        related_name='settings',
        on_delete=models.CASCADE,
    )
    launch = JSONField(default=default_launch_dict)
    team_communication = models.BooleanField(default=False)
    ask_to_ecosystem = models.BooleanField(default=False)
    swarm_session = models.BooleanField(default=False)
    directory = models.BooleanField(default=True)
    advisor_request = models.BooleanField(default=False)
    quizes = models.BooleanField(default=False)
    feedback = models.BooleanField(default=False)

    def __str__(self):
        return str(self.project)
