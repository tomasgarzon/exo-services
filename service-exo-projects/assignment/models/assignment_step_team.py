from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin

from .mixins import UploadedFileMixin


class AssignmentStepTeam(
        CreatedByMixin,
        UploadedFileMixin,
        TimeStampedModel):

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

    def __str__(self):
        return '{} - {}'.format(self.assignment_step.project, self.team.name)

    @property
    def project(self):
        return self.assignment_step.project

    @property
    def members(self):
        pass

    @property
    def stream(self):
        return self.team.stream

    def can_upload_files(self, user, raise_exception=True):
        return self.team.project.user_is_admin or user in self.team.members

    def can_view_uploaded_file(self, user, raise_exception=True):
        return self.team.project.user_is_admin\
            or self.team.project.user_is_readonly\
            or user in self.team.members

    def can_update_uploaded_file(self, user, uploaded_file_version, raise_exception=True):
        return self.can_upload_files(user, raise_exception)

    def can_delete_uploaded_file(self, user, uploaded_file, raise_exception=True):
        return self.can_upload_files(user, raise_exception)
