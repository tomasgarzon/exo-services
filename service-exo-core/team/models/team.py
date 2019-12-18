import uuid

from model_utils.models import TimeStampedModel
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from files.models import Resource
from permissions.models import PermissionManagerMixin
from permissions.shortcuts import has_team_perms
from project.models import Project
from utils.models import CreatedByMixin, TagAutoSlugField
from zoom_project.models.zoom_mixin import ZoomifyMixin

from ..conf import settings
from ..managers import TeamManager
from .team_mixins import TeamCoachMixin, TeamMemberMixin
from .team_member import TeamMemberManager


def create_slug_team(instance):
    return '{} {}'.format(instance.name, instance.get_stream_display())


class Team(
        PermissionManagerMixin,
        TeamCoachMixin,
        TeamMemberMixin,
        ZoomifyMixin,
        CreatedByMixin,
        TimeStampedModel):
    """
    Teams for Sprints work
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='teams',
    )

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)

    name = models.CharField(
        verbose_name='Team name',
        max_length=150,
    )

    stream = models.CharField(
        verbose_name='Stream',
        max_length=1,
        choices=settings.PROJECT_STREAM_CH_TYPE,
        default=settings.PROJECT_STREAM_CH_TYPE_DEFAULT,
    )
    slug = TagAutoSlugField(
        populate_from=create_slug_team,
        always_update=True,
        unique=True,
        tag_model=Resource,
    )
    coach = models.ForeignKey(
        'consultant.Consultant',
        related_name='teams_coach',
        on_delete=models.CASCADE,
        verbose_name='ExO Coach',
    )

    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='teams',
        blank=True,
    )

    _room = GenericRelation(
        'zoom_project.ZoomRoom',
        related_query_name='teams')

    posts = GenericRelation(
        'forum.Post',
        related_query_name='teams')

    objects = TeamManager()

    SEARCHEABLE_FIELDS = ['name']

    class Meta:
        verbose_name_plural = 'Teams'
        verbose_name = 'Team'
        permissions = settings.TEAM_ALL_PERMISSIONS
        ordering = ['name']

    def __str__(self):
        return str('%s ' % self.name)

    def send_notification(self, invitation):
        """
            Create notifications, for now only send an email
        """
        return None

    def activate(self, user):
        """
        Members and coach for this Model will be always active by
        default, so we don't need to activate
        """
        self.add_permission(settings.TEAM_PERMS_FULL_VIEW_TEAM, user)

    def deactivate(self, invitation, description=None):
        """
        Members and coach for this Model will be always active by
        default, so we don't need to activate
        """
        pass

    def get_public_url(self, invitation):
        """
        """
        return ''

    def add_resource(self, resource):
        resource.tags.add(self.slug)

    def remove_resource(self, resource):
        resource.tags.remove(self.slug)

    def has_perm(self, user, permission):
        return has_team_perms(self, permission, user)

    @property
    def has_meeting_id(self):
        return self.room.host_meeting_id is not None if self.room else ''

    @property
    def _zoom_settings(self):
        return self.project.zoom_settings

    def zoom_url(self, user_from):
        zoom_url = self.join_url

        if has_team_perms(
            self,
            settings.TEAM_PERMS_COACH_TEAM,
            user_from,
        ):
            zoom_url = self.start_url

        return zoom_url

    @property
    def members(self):
        if not hasattr(self, '_members'):
            self._members = TeamMemberManager(self)
        return self._members

    def check_user_can_post(self, user_from):
        return has_team_perms(
            self,
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            user_from)
