import inflection

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from model_utils.models import TimeStampedModel

from ..conf import settings
from ..managers.consultant_validation_status import ConsultantValidationStatusManager


class ConsultantValidationStatus(TimeStampedModel):
    """
    This model determines milestones which have to be completed by
    Consultants to active his profile at the Platform
    """

    CH_DEFAULT = settings.CONSULTANT_VALIDATION_CH_WAITING

    validation = models.ForeignKey(
        'consultant.ConsultantValidation',
        related_name='validations',
        on_delete=models.CASCADE,
    )
    consultant = models.ForeignKey(
        'consultant.Consultant',
        related_name='validations',
        on_delete=models.CASCADE,
    )
    user_from = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='consultants_validations',
    )
    status = models.CharField(
        max_length=1, default=CH_DEFAULT,
        choices=settings.CONSULTANT_VALIDATION_CH_STATUS,
        blank=False, null=False,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True, null=True,
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey(
        'content_type', 'object_id',
    )
    _description = models.TextField(blank=True, null=True)
    objects = ConsultantValidationStatusManager()

    class Meta:
        unique_together = (('validation', 'consultant'), )

    def __str__(self):
        return str('%s - %s: %s' % (
            self.consultant,
            self.validation,
            self.get_status_display(),
        ))

    @property
    def validation_type_display(self):
        return self.validation.get_name_display()

    @property
    def validation_type(self):
        return self.validation.name

    @property
    def is_user(self):
        return self.validation.is_user

    @property
    def is_profile(self):
        return self.validation.is_profile

    @property
    def is_agreement(self):
        return self.validation.is_agreement

    @property
    def is_skill_assessment(self):
        return self.validation.is_skill_assessment

    @property
    def is_application(self):
        return self.validation.is_application

    @property
    def is_test(self):
        return self.validation.is_test

    @property
    def is_skipped(self):
        return self.status == settings.CONSULTANT_VALIDATION_CH_SENT_SKIPPED

    @property
    def is_sent(self):
        return self.status == settings.CONSULTANT_VALIDATION_CH_SENT

    @property
    def is_validated(self):
        return self.status == settings.CONSULTANT_VALIDATION_CH_ACCEPTED

    @property
    def is_declined(self):
        return self.status == settings.CONSULTANT_VALIDATION_CH_DENIED

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    def validate(self):
        self.status = settings.CONSULTANT_VALIDATION_CH_ACCEPTED
        self.save(update_fields=['status', 'modified'])

    def validate_related_object(self, user_from, **kwargs):
        if self.content_object:
            self.content_object.accept(user_from, **kwargs)

    def activate(self, user_from, **kwargs):
        self.validate()
        self.validate_related_object(user_from, **kwargs)

    def cancel(self):
        self.status = settings.CONSULTANT_VALIDATION_CH_DENIED
        self.save(update_fields=['status', 'modified'])

    def deactivate(self, user_from, description=None):
        self.cancel()
        self.cancel_related_object(user_from, description)

    def cancel_related_object(self, user_from, description=None):
        if self.content_object:
            self.content_object.cancel(user_from, description)

    def reactivate(self, user_from):
        self.status = settings.CONSULTANT_VALIDATION_CH_WAITING
        self.save(update_fields=['status', 'modified'])

    def send_notification(self, invitation, *args, **kwargs):
        """
        Call to the validation send notification in order to send the
        corresponding notification email related with it's own type
        """
        sent = self.validation.send_notification(self, invitation, *args, **kwargs)
        if sent:
            self._notification_sent()

    def skip_notification(self):
        self.status = settings.CONSULTANT_VALIDATION_CH_SENT_SKIPPED
        self.save(update_fields=['status', 'modified'])

    def get_public_url(self, invitation):
        """
        Get the url for the validation
        """
        return self.validation.get_public_url(invitation)

    def _notification_sent(self):
        self.status = settings.CONSULTANT_VALIDATION_CH_SENT
        self.save(update_fields=['status', 'modified'])

    def generate_agreement(self, invitation):
        if self.content_object:
            raise ValidationError('You should remove related object before assign a new one')
        self.content_object = self.consultant.add_user_agreement()
        self.save(update_fields=['object_id', 'content_type'])

    def generate_user(self, invitation):
        if self.content_object:
            raise ValidationError('You should remove related object before assign a new one')
        self.content_object = self.consultant.user
        self.save(update_fields=['object_id', 'content_type'])

    def generate_onboarding(self, invitation):
        if self.content_object:
            raise ValidationError('You should remove related object before assign a new one')
        self.content_object = self.consultant
        self.save(update_fields=['object_id', 'content_type'])

    def generate_related_object(self, invitation):
        # calling to a method associated with each type of validation (if exists)
        validation_name = inflection.underscore(str(self.validation).replace(' ', ''))
        method_name = 'generate_' + validation_name
        if getattr(self, method_name, None):
            method = getattr(self, method_name)
            return method(invitation)
        return None

    def get_name_display(self):
        return self.validation.get_name_display()
