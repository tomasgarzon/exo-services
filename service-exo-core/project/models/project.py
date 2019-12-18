import uuid

from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation

from guardian.shortcuts import get_users_with_perms
from model_utils.models import TimeStampedModel
from autoslug import AutoSlugField

from files.models import Resource
from permissions.models import PermissionManagerMixin
from validation.validators.project import ProjectValidator
from validation.validators.creation_date import CreationDateValidator
from utils.descriptors import ChoicesDescriptorMixin
from permissions.objects import get_team_for_user
from utils.models import CreatedByMixin
from utils.mixins import LocationTimezoneMixin
from utils.dates import localize_date
from job.mixins import JobMixin

from ..managers.project import ProjectManager
from .step_mixin import StepMixin
from .mixins import (
    AssignmentProjectMixin, ResourceLibraryMixin,
    ProjectExecutionMixin, ProjectPermissions, ProjectCustomize, ProjectUpdateMixin)
from ..conf import settings


class Project(
        PermissionManagerMixin,
        ProjectUpdateMixin,
        ProjectCustomize,
        ProjectPermissions,
        ProjectExecutionMixin,
        StepMixin,
        AssignmentProjectMixin,
        ResourceLibraryMixin,
        ChoicesDescriptorMixin,
        LocationTimezoneMixin,
        JobMixin,
        CreatedByMixin,
        TimeStampedModel
):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=1,
        choices=settings.PROJECT_CH_PROJECT_STATUS,
        default=settings.PROJECT_CH_PROJECT_STATUS_DRAFT,
    )
    customer = models.ForeignKey(
        'customer.Customer',
        on_delete=models.PROTECT,
        related_name='projects',
        null=True,
    )
    consultants = models.ManyToManyField(
        'consultant.Consultant',
        through='relation.ConsultantProjectRole',
        related_name='projects',
        blank=True,
    )
    partners = models.ManyToManyField(
        'partner.Partner',
        through='relation.PartnerProjectRole',
        related_name='projects',
        blank=True,
    )
    slug = AutoSlugField(
        populate_from='name',
        always_update=False,
        null=True,
        blank=False,
        unique=True,
    )
    duration = models.IntegerField(null=True)
    agenda = models.URLField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    template = models.CharField(
        'Template or project type',
        max_length=100,
        default='',
        null=True, blank=True)
    internal_organization = models.ForeignKey(
        'custom_auth.InternalOrganization',
        blank=True, null=True,
        default=None,
        related_name='projects',
        on_delete=models.CASCADE,
    )
    credentials = GenericRelation(
        'certification.CertificationGroup',
        related_query_name='projects')
    category = models.CharField(
        max_length=2,
        choices=settings.PROJECT_CH_CATEGORY,
        default=settings.PROJECT_CH_CATEGORY_DEFAULT,
    )
    CHOICES_DESCRIPTOR_FIELDS = [
        'status',
        'type_project_lower',
    ]
    CHOICES_DESCRIPTOR_FIELDS_CHOICES = [
        settings.PROJECT_CH_PROJECT_INTERNAL_STATUS,
        settings.PROJECT_CH_TYPE_PROJECT,
    ]

    objects = ProjectManager()

    class Meta:
        verbose_name_plural = 'Projects'
        verbose_name = 'Project'
        permissions = settings.PROJECT_ALL_PERMISSIONS
        ordering = ['name']

    def __str__(self):
        return str(self.name)

    @property
    def is_version_2(self):
        return self.settings.version == settings.PROJECT_CH_VERSION_2

    @property
    def is_training(self):
        return self.customer and self.customer.customer_type == settings.CUSTOMER_CH_TRAINING

    @property
    def is_job_hidden(self):
        return self.project_settings.hide_from_my_jobs

    @property
    def start_localize(self):
        return localize_date(self.start, self.timezone) if self.start else ''

    @property
    def end_localize(self):
        return localize_date(self.end, self.timezone) if self.end else ''

    def clean(self):
        if self.start is not None and self.end is not None:
            if self.start > self.end:
                raise ValidationError({
                    'start': ValidationError('Invalid date', code='invalid'),
                })

    @property
    def organization(self):
        try:
            organization = self.customer.organization
        except ObjectDoesNotExist:
            organization = None
        return organization

    @property
    def users(self):
        return self.users_roles.all().users()

    @property
    def real_type(self):
        real_type = self
        for _, type_project in settings.PROJECT_CH_TYPE_PROJECT:
            if hasattr(self, type_project):
                real_type = getattr(self, type_project)
                break
        return real_type

    @property
    def type_project(self):
        return self.real_type.__class__.__name__

    @property
    def type_project_lower(self):
        return self.type_project.lower()

    @property
    def type_verbose_name(self):
        return self.real_type.__class__._meta.verbose_name

    @classmethod
    def type(cls):
        return cls.__name__.lower()

    @property
    def project_manager(self):
        project_manager = None
        consultant_project_roles_roles = self.consultants_roles.get_project_manager_consultants(self)

        if consultant_project_roles_roles:
            project_manager = consultant_project_roles_roles[0].consultant

        return project_manager

    @property
    def delivery_managers(self):
        return [
            user for user, perms in
            get_users_with_perms(self, attach_perms=True, with_group_users=False).items()
            if settings.PROJECT_PERMS_DELIVERY_MANAGER in perms
        ]

    @property
    def can_be_finished(self):
        return not self.is_finished and self.is_started

    @property
    def can_be_started(self):
        return self.is_waiting or self.is_draft

    @property
    def can_be_launch(self):
        return self.is_draft and self.real_type.allowed_access

    @property
    def folder(self):
        folder_name = '{}_{}'.format(settings.PROJECT_FOLDER_PREFIX, self.id)
        return folder_name

    @property
    def customer_members(self):
        return self.customer.users.all()

    @property
    def partner(self):
        return self.partners.first()

    @partner.setter
    def partner(self, value):
        if self.partner != value:
            self.partners.clear()
            self.partners_roles.create(
                partner=value,
            )

    @property
    def profile_url(self):
        return settings.FRONTEND_PROJECT_PROFILE_PAGE.format(
            **{'section': 'information', 'slug': self.slug})

    def autosend(self, consultant=False):
        project_settings = self.settings
        if consultant:
            welcome = project_settings.launch['send_welcome_consultant']
        else:
            welcome = project_settings.launch['send_welcome_participant']
        return not self.is_draft and welcome

    @property
    def autoactive(self):
        return not self.is_draft

    def get_absolute_url(self):
        url = reverse('project:project:dashboard', kwargs={'project_id': self.id})
        if not self.is_version_2:
            url = settings.SERVER_VERSION_1 + url
        return url

    @property
    def resources(self):
        q1 = models.Q(tags__name=settings.FILES_GENERAL_TAG)
        q2 = models.Q(tags__name=self.slug)
        return Resource.objects.filter(q1).filter(q2).exclude(
            tags__name=settings.FILES_HIDE_TAG,
        )

    @property
    def supported_version(self):
        date_validator = CreationDateValidator(self)
        return date_validator.validate()

    @staticmethod
    def validator_class():
        return ProjectValidator

    @property
    def allowed_access(self):
        validator = self.__class__.validator_class()(self)
        validator.validate()

        return self.validations.filter_by_validation_type_error().filter_by_status_pending().count() == 0

    def get_frontend_index_url(self, user=None):
        return self.get_frontend_version_2_url(user) if self.is_version_2 else self.get_frontend_version_1_url()

    def get_frontend_version_2_url(self, user=None):
        url = None
        if self.is_version_2:
            step = self.current_step()
            if user is None:
                team = self.teams.first()
            else:
                team = get_team_for_user(self, user).first()
            if step and team:
                url = settings.FRONTEND_PROJECT_STEP_PAGE.format(
                    **{
                        'project_id': self.id,
                        'team_id': team.pk,
                        'step_id': step.pk,
                        'section': 'learn'})
            elif team and self.qa_sessions.exists():
                url = settings.FRONTEND_PROJECT_PAGE.format(
                    **{
                        'project_id': self.id,
                        'team_id': team.pk,
                        'section': 'swarm-session'})
        else:
            url = self.get_frontend_version_1_url()
        return url

    def get_frontend_version_1_url(self):
        return settings.SERVER_VERSION_1

    @property
    def need_job(self):
        is_start_defined = self.get_project_start_date() is not None

        return not self.is_draft and not self.is_job_hidden and is_start_defined
