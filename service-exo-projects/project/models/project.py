import uuid
import pytz

from django.db import models
from django.apps import apps
from django.core.management import call_command
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model

from model_utils.models import TimeStampedModel

from utils.permissions import PermissionManagerMixin
from utils.descriptors import ChoicesDescriptorMixin
from utils.models import CreatedByMixin
from utils.mixins import LocationMixin

from ..managers.project import ProjectManager
from .mixins import (
    ProjectExecutionMixin,
    ProjectPermissions,
    ProjectStepMixin,
    ProjectActions)
from ..conf import settings


class Project(
        PermissionManagerMixin,
        ProjectPermissions,
        ProjectExecutionMixin,
        ProjectStepMixin,
        ProjectActions,
        LocationMixin,
        ChoicesDescriptorMixin,
        CreatedByMixin,
        TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=1,
        choices=settings.PROJECT_CH_STATUS,
        default=settings.PROJECT_CH_STATUS_DRAFT,
    )
    content_template = models.CharField(
        max_length=20,
        choices=settings.PROJECT_CH_PROJECT_TEMPLATE,
        default=settings.PROJECT_CH_PROJECT_TEMPLATE_DEFAULT,
    )
    template_name = models.CharField(
        'Template or project type',
        max_length=100,
        default=settings.PROJECT_TEMPLATE_NAME_DEFAULT,
        null=True, blank=True)
    accomplish = models.CharField(
        max_length=1,
        choices=settings.PROJECT_CH_ACCOMPLISH,
        blank=True,
        null=True,
    )
    transform = models.CharField(
        max_length=1,
        choices=settings.PROJECT_CH_TRANSFORM,
        blank=True,
        null=True,
    )
    playground = models.CharField(
        max_length=1,
        choices=settings.PROJECT_CH_PLAYGROUND,
        blank=True,
        null=True,
    )
    customer = models.CharField(
        blank=True, null=True,
        max_length=255)
    comment = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=2,
        choices=settings.PROJECT_CH_CATEGORY,
        default=settings.PROJECT_CH_CATEGORY_DEFAULT,
    )
    permissions = GenericRelation(
        'guardian.UserObjectPermission',
        content_type_field='content_type',
        object_id_field='object_pk',
        related_query_name='projects')

    CHOICES_DESCRIPTOR_FIELDS = [
        'status',
        'content_template',
    ]
    CHOICES_DESCRIPTOR_FIELDS_CHOICES = [
        settings.PROJECT_CH_PROJECT_INTERNAL_STATUS,
        settings.PROJECT_CH_PROJECT_TEMPLATE,
    ]

    objects = ProjectManager()

    class Meta:
        permissions = settings.PROJECT_ALL_PERMISSIONS
        ordering = ['name']

    def __str__(self):
        return str(self.name)

    @property
    def timezone(self):
        return pytz.utc

    def get_assignments(self):
        AssignmentStep = apps.get_model(app_label='assignment', model_name='AssignmentStep')
        return AssignmentStep.objects.filter_by_project(self)

    @property
    def can_be_finished(self):
        return not self.is_finished and self.is_started

    @property
    def can_be_started(self):
        return self.is_waiting or self.is_draft

    @property
    def can_be_launch(self):
        return self.is_draft

    @property
    def members(self):
        return get_user_model().objects.filter(
            user_project_roles__project_role__project=self
        ).distinct()

    @property
    def collaborators(self):
        return get_user_model().objects.filter(
            user_project_roles__project_role__project=self
        ).exclude(
            user_project_roles__project_role__code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT
        ).distinct()

    @property
    def participants(self):
        return get_user_model().objects.filter(
            user_project_roles__project_role__project=self,
            user_project_roles__project_role__code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT
        ).distinct()

    def set_status(self, user, new_status):
        self.status = new_status
        self.save(update_fields=['status', 'modified'])
        self.statuses.create(created_by=user, status=new_status)

    def autosend(self, consultant=False):
        if consultant:
            welcome = self.settings.launch['send_welcome_consultant']
        else:
            welcome = self.settings.launch['send_welcome_participant']
        return not self.is_draft and welcome

    @property
    def head_coaches(self):
        return get_user_model().objects.filter(
            user_project_roles__project_role__project=self,
            user_project_roles__project_role__code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH
        ).distinct()

    @property
    def autoactive(self):
        return not self.is_draft

    def populate(self):
        call_command('populate_project', self.pk)

    def _remove_logical(self, user_from, comment=None):
        self.status = settings.PROJECT_CH_STATUS_REMOVED
        self.save(update_fields=['status', 'modified'])

    def remove(self, user_from, comment=None):
        self._remove_logical(user_from, comment)

    def url_zone(self, user):
        user_team_role = user.user_team_roles.filter(team__project=self).first()

        if not user_team_role:
            return settings.PROJECT_URL_PROFILE.format(self.id)

        team = user_team_role.team

        try:
            current_step = self.steps.filter(
                status=settings.PROJECT_CH_STATUS_STEP_CURRENT).get()
        except Exception:
            current_step = self.current_step()

        return settings.PROJECT_URL_ZONE.format(
            self.id,
            team.id,
            current_step.id)
