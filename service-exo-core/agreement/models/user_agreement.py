from django.db import models

from model_utils.models import TimeStampedModel

from consultant.models.consultant_validation_mixin import ConsultantValidationMixin
from utils.descriptors import ChoicesDescriptorMixin

from ..conf import settings
from ..managers.user_agreement import UserAgreementManager


class UserAgreement(
        ConsultantValidationMixin,
        ChoicesDescriptorMixin,
        TimeStampedModel
):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='agreements',
        on_delete=models.CASCADE,
    )
    agreement = models.ForeignKey(
        'agreement.Agreement',
        related_name='user_agreements',
        on_delete=models.CASCADE,
    )

    status = models.CharField(
        max_length=1,
        default=settings.AGREEMENT_USER_STATUS_DEFAULT,
        choices=settings.AGREEMENT_USER_STATUS,
        blank=False, null=False,
    )

    # Validation Object type
    validation_name = settings.CONSULTANT_VALIDATION_AGREEMENT

    CHOICES_DESCRIPTOR_FIELDS = ['status']

    objects = UserAgreementManager()

    class Meta:
        unique_together = ('user', 'agreement')

    def __str__(self):
        return '{} - {} - Status: {}'.format(
            self.user,
            self.agreement,
            self.get_status_display(),
        )

    @property
    def date_signed(self):
        return self.modified if self.is_accepted else None

    @property
    def date_revoked(self):
        return self.modified if self.is_revoked else None

    def _set_status(self, status):
        self.status = status
        self.save(update_fields=['status', 'modified'])

    def can_be_accepted(self):
        return self.agreement.is_active

    def revoke(self, user_from):
        self._set_status(settings.AGREEMENT_USER_STATUS_REVOKED)

    def activate(self, user_from, *args, **kwargs):
        return self.accept(user_from)

    def accept(self, user_from):
        if self.can_be_accepted():
            self._set_status(settings.AGREEMENT_USER_STATUS_SIGNED)

    def deactivate(self, user_from, description=None):
        self.revoke(user_from)

    def cancel(self, user_from, description=None):
        self.revoke(user_from)

    def send_notification(self, invitation, *args, **kwargs):
        pass

    def get_public_url(self, invitation):
        return ''
