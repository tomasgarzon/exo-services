from model_utils.models import TimeStampedModel

from django.db import models

from utils.models import CreatedByMixin

from .conf import settings
from .conversation_helper import create_group, update_group


class Group(CreatedByMixin, TimeStampedModel):
    conversation_uuid = models.UUIDField(blank=True, null=True)
    group_type = models.CharField(
        max_length=1,
        choices=settings.COMMUNICATION_CH_TYPE_CHOICES)
    project = models.ForeignKey(
        'project.Project',
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='groups')
    team = models.OneToOneField(
        'team.Team',
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='group')
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='communication_groups')

    def create(self, user_from):
        create_group(self, user_from)

    def update(self, user_from):
        update_group(self, user_from)

    def get_icon(self):
        if self.group_type == settings.COMMUNICATION_CH_GENERAL:
            return 'https://cdn.filestackcontent.com/VaLQ6i8SlaHZh9MBVLbA'
        elif self.group_type == settings.COMMUNICATION_CH_COLLABORATORS:
            return 'https://cdn.filestackcontent.com/N4Ggba1IRUGib03DvTBE'
        else:
            return self.team.image

    def get_name(self):
        if self.group_type == settings.COMMUNICATION_CH_GENERAL:
            return 'All Members'
        elif self.group_type == settings.COMMUNICATION_CH_COLLABORATORS:
            return 'Collaborators'
        else:
            return self.team.name

    @property
    def is_for_team(self):
        return self.group_type == settings.COMMUNICATION_CH_TEAM
