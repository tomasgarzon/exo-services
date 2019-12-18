from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings
from .mixins import ActionLogMixin


class UserBadge(ActionLogMixin, TimeStampedModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        on_delete=models.CASCADE,
    )
    badge = models.ForeignKey(
        'badge.Badge',
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        on_delete=models.CASCADE,
    )

    items = models.ManyToManyField(
        'UserBadge',
        through='UserBadgeItem',
        related_name='user_badges',
    )

    def __str__(self):
        return '{} - {}'.format(self.user.email, self.badge)

    @property
    def code(self):
        return self.badge.code

    @property
    def category(self):
        return self.badge.category

    @property
    def is_activity(self):
        return hasattr(self, 'userbadgeactivity')

    @property
    def is_job(self):
        return hasattr(self, 'userbadgejob')

    @property
    def num(self):
        if self.is_activity:
            num = 1
        else:
            num = self.user_badge_items.all().count()
        return num


class UserBadgeActivity(UserBadge):
    pass


class UserBadgeJob(UserBadge):
    pass


class UserBadgeItem(TimeStampedModel):
    user_badge = models.ForeignKey(
        'UserBadge',
        related_name='user_badge_items',
        on_delete=models.CASCADE,
    )

    name = models.CharField(max_length=255)
    date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.name
