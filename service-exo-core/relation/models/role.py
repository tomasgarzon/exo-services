from django.core.exceptions import ValidationError
from model_utils.models import TimeStampedModel
from django.db import models

from permissions.models import PermissionManagerMixin
from invitation.models import Invitation
from utils.descriptors import ChoicesDescriptorMixin

from ..conf import settings


class Role(ChoicesDescriptorMixin, PermissionManagerMixin, TimeStampedModel):

    status = models.CharField(
        max_length=1,
        choices=settings.RELATION_ROLE_CH_STATUS,
        default=settings.RELATION_ROLE_CH_INACTIVE,
    )
    visible = models.BooleanField(
        default=True)

    class Meta:
        abstract = True

    def can_activate(self, user_from):
        cond1 = user_from.has_perm(
            settings.RELATION_ACTIVE_ROLE,
            self,
        )
        cond2 = user_from.has_perm(
            self._perms_activate,
            getattr(self, self._related_object),
        )
        if not(cond1 or cond2):
            raise ValidationError(
                "User doesn't allow to active this role: ({} given)".format(user_from),
            )
        return True

    def can_deactivate(self, user_from):
        cond1 = user_from.has_perm(settings.RELATION_CANCEL_ROLE, self)
        cond2 = user_from.has_perm(
            self._perms_activate, getattr(self, self._related_object),
        )
        if not(cond1 or cond2):
            raise ValidationError(
                "User doesn't allow to deactive this role: ({} given)".format(user_from),
            )
        return True

    def activate(self, user_from):
        if not self.is_active:
            self.can_activate(user_from)
            self.status = settings.RELATION_ROLE_CH_ACTIVE
            self.save(update_fields=['status'])

    def deactivate(self, user_from, description=None):
        if self.is_active:
            self.can_deactivate(user_from)
            self.status = settings.RELATION_ROLE_CH_INACTIVE
            self.save(update_fields=['status'])

    @property
    def invitation(self):
        try:
            return Invitation.objects.filter_by_object(self).get()
        except Invitation.DoesNotExist:
            return None

    @property
    def need_job(self):

        try:
            has_swarm = self.qa_session_advisors.all().exists()
        except AttributeError:
            has_swarm = False

        return self.is_active and self.project.need_job and not has_swarm
