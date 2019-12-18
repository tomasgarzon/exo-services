from datetime import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from model_utils.models import TimeStampedModel
from model_utils.fields import MonitorField, StatusField

from permissions.models import PermissionManagerMixin
from utils.random import build_name
from utils.descriptors import ChoicesDescriptorMixin
from registration.models.registration_process import RegistrationProcess

from ..conf import settings
from ..managers import InvitationManager, InvitationPendingManager
from .invitation_object import InvitationObject
from .mixins import ExtraDataInvitationMixin


class Invitation(
        PermissionManagerMixin,
        ChoicesDescriptorMixin,
        ExtraDataInvitationMixin,
        TimeStampedModel
):

    INVITATION_CH_STATUS = settings.INVITATION_CH_STATUS

    status = StatusField(
        choices_name='INVITATION_CH_STATUS',
        default=settings.INVITATION_STATUS_CH_PENDING,
    )
    status_changed = MonitorField(monitor='status')

    type = models.CharField(
        max_length=1,
        choices=settings.INVITATION_CH_TYPE,
    )

    hash = models.CharField(
        max_length=512, blank=False,
        null=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='invitations',
        on_delete=models.CASCADE,
    )
    invite_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='This user creates the invitation to user',
        related_name='invitations_from',
        blank=True, null=True,
        on_delete=models.CASCADE,
    )

    # Date until this invitation is valid
    valid_date = models.DateField(blank=True, null=True)
    _description = models.TextField(blank=True, null=True)
    description_response = models.TextField(blank=True, null=True)

    # Scope of invitation
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        blank=True, null=True,
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    scope = GenericForeignKey('content_type', 'object_id')

    objects = InvitationManager()
    pendings = InvitationPendingManager()

    invitation_detail_class = InvitationObject

    CHOICES_DESCRIPTOR_FIELDS = ['status', 'type']

    class Meta:
        verbose_name_plural = 'Invitations'
        verbose_name = 'Invitation'
        permissions = settings.INVITATION_ALL_PERMISSIONS

    def __str__(self):
        return '%s [%s]: %s - %s' % (
            self.user,
            self.get_type_display(),
            self.invitation_related,
            self.get_status_display(),
        )

    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = build_name()
        return super(Invitation, self).save(*args, **kwargs)

    @property
    def validation_object(self):
        validation = None
        if self.invitation_related.is_validation:
            validation = self.invitation_related.content_object

        return validation

    @property
    def has_registration(self):
        registration = None
        if self.user.is_consultant and self.validation_object:
            try:
                registration_process = self.user.registration_process
                if registration_process.get_step_for_object(self.validation_object):
                    registration = registration_process
            except RegistrationProcess.DoesNotExist:
                pass

        return registration

    @property
    def registration_step(self):
        """
        Return the Step object related with this invitation is exist
        """
        registration_step = None
        registration = self.has_registration
        if registration:
            registration_step = registration.get_step_for_object(self.validation_object)

        return registration_step

    @property
    def description(self):
        for related in self.invitation_objects.all():
            if hasattr(related.content_object, 'description'):
                return related.content_object.description
        return self._description

    @description.setter
    def description(self, value):
        related_description = False
        for related in self.invitation_objects.all():
            if hasattr(related.content_object, 'description'):
                related.content_object.description = value
                related.content_object.save()
                related_description = True
                break
        if not related_description:
            self._description = value

    # ## PERMISSIONS ###
    def check_permission(self, user, permission, raise_errors=False, message='{}'):
        user_perm = user.has_perm(permission, self)
        scope_perm = self.scope and self.scope.has_perm(user, permission)
        if not user_perm and not scope_perm:
            if raise_errors:
                raise ValidationError(message.format(user))
            else:
                return False
        return True

    def can_be_accepted(self, user, raise_errors=False):
        """
            Check if the invitation can be accepted by user
        """
        permission = self.check_permission(
            user,
            settings.INVITATION_ACCEPT,
            raise_errors=raise_errors,
            message="User doesn't allow to accept the invitation: ({} given)",
        )
        if not permission:
            return permission

        if not self.validate_date:
            if raise_errors:
                raise ValidationError(
                    'Invitation date expired'.format(self.valid_date),
                )
            else:
                return False
        return True

    def set_status(self, user, status):
        self.status = status
        self.save(update_fields=['status', 'modified'])
        self.add_log_status(user)

    def add_log_status(self, user):
        self.logs.create(
            user=user,
            log_type=settings.INVITATION_CH_TYPE_LOG_STATUS,
            description='Changed to: {}'.format(self.get_status_display()),
        )

    def add_log_send(self, user):
        self.logs.create(
            user=user,
            log_type=settings.INVITATION_CH_TYPE_LOG_SEND,
        )

    # ## OPERATIONS ###
    def accept(self, user, **kwargs):
        """
        Change status to CH_ACTIVE
        The param 'user' determine who is doing the action
        """
        self.can_be_accepted(user, raise_errors=True)
        self.set_status(user, settings.INVITATION_STATUS_CH_ACTIVE)
        for related in self.invitation_objects.all():
            related.activate(user, **kwargs)

    def can_be_cancelled(self, user, raise_errors=False):
        return self.check_permission(
            user,
            settings.INVITATION_CANCEL,
            raise_errors=raise_errors,
            message="User doesn't allow to cancel the invitation: ({} given)",
        )

    def cancel(self, user, description=None):
        """
        Change status to CH_CANCELLED
        The param 'user' determine who is doing the action
        """
        self.can_be_cancelled(user, raise_errors=True)

        if description:
            self.description_response = description
            update_fields = ['description_response']
            self.save(update_fields=update_fields)

        self.set_status(user, settings.INVITATION_STATUS_CH_CANCELLED)

        for related in self.invitation_objects.all():
            related.deactivate(user, description)

    def reactivate(self, user, description=None, autosend=True):
        """
        Change status to CH_PENDING
        The param 'user' determine who is doing the action
        """
        self.check_permission(
            user,
            settings.INVITATION_CANCEL,
            raise_errors=True,
            message="User doesn't allow to cancel/reactivate the invitation: ({} given)",
        )

        self.set_status(user, settings.INVITATION_STATUS_CH_PENDING)

        for related in self.invitation_objects.all():
            related.reactivate(user, description)
            if autosend:
                related.send_notification(user)

    def resend(self, user):
        """
        Resend email for invitation
        The param 'user' determine who is doing the action
        """
        self.check_permission(
            user,
            settings.INVITATION_RESEND,
            raise_errors=True,
            message="User doesn't allow to resend the invitation: ({} given)",
        )
        for related in self.invitation_objects.all():
            related.send_notification(user)

    @property
    def validate_date(self):
        """
        Validates if the validation date for invitation is still available
        """
        if self.valid_date is None:
            return True
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        return today <= self.valid_date

    @classmethod
    def is_consultant_validation_type(cls, invitation_type):
        VALIDATION_TYPE = [
            code
            for code, _ in
            settings.CONSULTANT_VALIDATION_CH_TYPE
        ]
        return invitation_type in VALIDATION_TYPE

    @property
    def invitation_related(self):
        return self.invitation_objects.first()
