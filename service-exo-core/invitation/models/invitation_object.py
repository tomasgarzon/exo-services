from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from model_utils.models import TimeStampedModel


class InvitationObject(TimeStampedModel):

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    invitation = models.ForeignKey(
        'invitation.Invitation',
        related_name='invitation_objects',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '%s' % self.content_object

    @property
    def is_validation(self):
        Invitation = self.invitation.__class__
        return Invitation.is_consultant_validation_type(self.invitation.type)

    @property
    def related_invitation_type(self):
        return self.content_object.validation.name

    def activate(self, user_from, **kwargs):
        """
            Activate the related object associated to the invitation
        """
        self.content_object.activate(user_from, **kwargs)

    def deactivate(self, user_from, description=None):
        """
            Activate the related object associated to the invitation
        """
        self.content_object.deactivate(user_from, description)

    def reactivate(self, user_from, description=None):
        # Reactivate means change to WAITING
        self.content_object.reactivate(user_from)

    def send_notification(self, user):
        """
            Send notifiction associated to the content_object
        """
        self.content_object.send_notification(self.invitation)
        self.invitation.add_log_send(user)

    def skip_notification(self):
        has_attr = hasattr(self.content_object, 'skip_notification')
        is_callable = callable(getattr(
            self.content_object,
            'skip_notification', '',
        ))
        if has_attr and is_callable:
            self.content_object.skip_notification()
