from django.apps import apps
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth import get_user_model

from certification.signals_define import accredible_certification_created

from relation.models import UserProjectRole
from relation.signals_define import signal_user_assigned

from ..signals_define import (  # noqa
    signal_update_consultant_status
)
from .consultant import consultant_post_save_perms
from .consultant_hubspot import (
    accredible_certification_created_handler,
    update_user_email_at_hubspot,
    update_user_foundations_joining_date
)
from .consultant_status_signal import post_save_user, update_consultant_status
from .consultant_validation_status_signal import post_save_consultant_validation_status
from .consultant_update_profile import (
    post_save_update_languages,
    post_save_update_keywords,
    post_save_update_user_redis,
)


def setup_signals():
    Consultant = apps.get_model(
        app_label='consultant',
        model_name='Consultant',
    )
    ConsultantValidationStatus = apps.get_model(
        app_label='consultant', model_name='ConsultantValidationStatus',
    )
    EmailAddress = apps.get_model(
        'exo_accounts',
        'EmailAddress'
    )

    post_save.connect(post_save_user, sender=get_user_model())
    post_save.connect(consultant_post_save_perms, sender=Consultant)
    post_save.connect(
        post_save_consultant_validation_status,
        sender=ConsultantValidationStatus,
    )
    signal_update_consultant_status.connect(update_consultant_status)
    models.signals.m2m_changed.connect(
        post_save_update_languages,
        sender=Consultant.languages.through,
    )
    post_save.connect(
        post_save_update_keywords,
        sender=Consultant._industries.through,
    )
    post_save.connect(
        post_save_update_keywords,
        sender=Consultant._exo_attributes.through,
    )
    post_save.connect(
        post_save_update_keywords,
        sender=Consultant._keywords.through,
    )
    post_save.connect(
        post_save_update_user_redis,
        sender=get_user_model(),
    )

    # HubSpot
    post_save.connect(update_user_email_at_hubspot, sender=EmailAddress)
    signal_user_assigned.connect(
        update_user_foundations_joining_date,
        sender=UserProjectRole,
    )

    # Acreedible certifications
    accredible_certification_created.connect(
        accredible_certification_created_handler
    )
