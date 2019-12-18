from django.apps import apps
from django.db.models.signals import post_save

from .invitation_status_changed import when_invitation_registration_post_save
from .consultant_validation_status_changed import when_consultant_validation_status_update


def setup_signals():
    Invitation = apps.get_model(
        app_label='invitation',
        model_name='Invitation',
    )
    ConsultantValidationStatus = apps.get_model(
        app_label='consultant',
        model_name='ConsultantValidationStatus',
    )

    post_save.connect(
        when_invitation_registration_post_save,
        sender=Invitation,
    )
    post_save.connect(
        when_consultant_validation_status_update,
        sender=ConsultantValidationStatus,
    )
