from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from actstream.actions import follow, unfollow
from actstream.models import followers, Follow
from model_utils.models import TimeStampedModel
import autoslug.fields

from permissions.models import PermissionManagerMixin
from utils.models import CreatedByMixin

from ..conf import settings
from ..managers import CircleManager, CircleAllManager
from .circle_metric import CircleMetricMixin


class Circle(
        PermissionManagerMixin,
        CircleMetricMixin,
        CreatedByMixin,
        TimeStampedModel):

    name = models.CharField(max_length=200)
    slug = autoslug.fields.AutoSlugField(
        populate_from='name',
        unique=True,
    )
    description = models.TextField(blank=True, null=True)
    hub = models.OneToOneField(
        'exo_hub.ExOHub',
        related_name='circle',
        on_delete=models.SET_NULL,
        blank=True, null=True)
    code = models.CharField(
        max_length=1,
        blank=True, null=True)
    image = models.CharField(
        max_length=255,
        blank=True, null=True)
    posts = GenericRelation('forum.Post')
    tags = models.ManyToManyField('keywords.Keyword')
    type = models.CharField(
        max_length=1,
        choices=settings.CIRCLES_CH_TYPES,
        default=settings.CIRCLES_CH_TYPE_OPEN,
    )
    certification_required = models.ForeignKey(
        'exo_role.CertificationRole',
        blank=True, null=True,
        on_delete=models.SET_NULL)
    removed = models.BooleanField(default=False)

    objects = CircleManager()
    all_objects = CircleAllManager()

    class Meta:
        verbose_name = 'Circle'
        verbose_name_plural = 'Circle'
        permissions = settings.CIRCLES_ALL_PERMISSIONS
        ordering = ['name']

    def __str__(self):
        return self.name

    def add_user(self, user):
        self.add_permission(
            settings.CIRCLES_PERMS_CREATE_POST,
            user,
        )
        follow(user, self)

    def remove_user(self, user):
        self.remove_permission(
            settings.CIRCLES_PERMS_CREATE_POST,
            user,
        )
        unfollow(user, self, send_action=True)

    def mark_as_removed(self):
        self.removed = True
        self.save(update_fields=['removed'])

    # PERMISSIONS
    def user_status(self, user_from):
        if self.is_user_in_followers(user_from):
            return settings.CIRCLES_CH_USER_STATUS_MEMBER
        else:
            return settings.CIRCLES_CH_USER_STATUS_GUEST

    def user_can_join(self, user_from, raise_exceptions=True):
        if self.is_open:
            return True
        if raise_exceptions:
            raise PermissionError
        return False

    def user_can_leave(self, user_from, raise_exceptions=True):
        is_follower = self.is_user_in_followers(user_from)
        if is_follower and not self.is_certified and self.created_by != user_from:
            return True
        if raise_exceptions:
            raise PermissionError
        return False

    def can_edit(self, user_from, raise_exceptions=True):
        if user_from.is_superuser or user_from == self.created_by:
            return True
        if raise_exceptions:
            raise PermissionError
        return False

    def check_user_can_post(self, user_from, raise_exceptions=True):
        if user_from.has_perm(settings.CIRCLES_PERMS_CREATE_POST, self):
            return True
        if raise_exceptions:
            raise PermissionError
        return False

    @property
    def total_members(self):
        return Follow.objects.followers_qs(self).count()

    @property
    def url(self):
        return settings.FRONTEND_CIRCLE_DETAIL_PAGE.format(
            slug=self.slug)

    @property
    def is_open(self):
        return self.type == settings.CIRCLES_CH_TYPE_OPEN

    @property
    def is_certified(self):
        return self.type == settings.CIRCLES_CH_TYPE_CERTIFIED

    @property
    def is_guest_readable(self):
        public_read_only = [
            settings.CIRCLES_CH_TYPE_OPEN,
            settings.CIRCLES_CH_TYPE_PUBLIC,
        ]
        return self.type in public_read_only

    @property
    def followers(self):
        return followers(self)

    def is_user_in_followers(self, user):
        return Follow.objects.followers_qs(self).filter(user=user).exists()
