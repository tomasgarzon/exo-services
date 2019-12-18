from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel

from utils.descriptors import ChoicesDescriptorMixin

from ...managers.consultant_exo_activity import ConsultantExOActivityManager


class ConsultantActivity(ChoicesDescriptorMixin, TimeStampedModel):

    consultant_profile = models.ForeignKey(
        'consultant.ConsultantExOProfile',
        related_name='exo_activities',
        on_delete=models.CASCADE,
    )
    exo_activity = models.ForeignKey(
        'exo_activity.ExOActivity',
        related_name='consultants',
        on_delete=models.CASCADE,
    )

    status = models.CharField(
        max_length=1,
        default=settings.RELATION_ACTIVITY_STATUS_CH_DEFAULT,
        choices=settings.RELATION_ACTIVITY_STATUS_CHOICES,
        blank=False, null=False,
    )

    objects = ConsultantExOActivityManager()

    class Meta:
        verbose_name_plural = 'Consultant Activities'
        verbose_name = 'Consultant Activity'

    def __str__(self):
        return '{} - {} - [{}]'.format(
            self.consultant_profile.consultant,
            self.exo_activity,
            self.get_status_display(),
        )

    @property
    def permission(self):
        return self.exo_activity.perm

    @property
    def user(self):
        return self.consultant_profile.consultant.user

    def should_be_reactivated(self, get_or_create_created_flag):
        return not get_or_create_created_flag and (self.is_disabled or self.is_pending)

    def _set_status(self, status):
        self.status = status
        self.save(update_fields=['status', 'modified'])

    def enable(self):
        if not self.is_enabled:
            self._set_status(settings.RELATION_ACTIVITY_STATUS_CH_ACTIVE)

    def disable(self):
        if not self.is_disabled:
            self._set_status(settings.RELATION_ACTIVITY_STATUS_CH_DISABLED)

    def add_permissions_related_to_activity(self):
        self.user.user_permissions.add(
            self.exo_activity.perm,
        )

    def remove_permissions_related_to_activity(self):
        self.user.user_permissions.remove(
            self.exo_activity.perm,
        )
