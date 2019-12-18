from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from model_utils.models import TimeStampedModel

from files.mixins import UploadedFileMixin
from permissions.shortcuts import has_team_perms
from utils.models import CreatedByMixin


class AssignmentStepTeam(
        UploadedFileMixin,
        CreatedByMixin,
        TimeStampedModel,
):

    assignment_step = models.ForeignKey(
        'AssignmentStep',
        related_name='assignment_step_teams',
        on_delete=models.CASCADE)
    team = models.ForeignKey(
        'team.Team',
        related_name='assignment_step_teams',
        on_delete=models.CASCADE)
    files = GenericRelation('files.UploadedFile')
    files_with_visibility = GenericRelation('files.UploadedFileVisibility')

    class Meta:
        unique_together = ('assignment_step', 'team')

    def __str__(self):
        return '{} - {}'.format(self.assignment_step.project, self.team.name)

    @property
    def project(self):
        return self.assignment_step.project

    @property
    def members(self):
        return self.team.team_members

    @property
    def stream(self):
        return self.team.stream

    def can_upload_files(self, user, raise_exception=True):
        return has_team_perms(
            self.team,
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            user,
        )

    def can_view_uploaded_file(self, user, raise_exception=True):
        return has_team_perms(
            self.team,
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            user,
        )

    def can_update_uploaded_file(self, user, uploaded_file_version, raise_exception=True):
        return has_team_perms(
            self.team,
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            user,
        )

    def can_delete_uploaded_file(self, user, uploaded_file, raise_exception=True):
        return has_team_perms(
            self.team,
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            user,
        )
