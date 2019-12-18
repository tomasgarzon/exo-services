from certification.signals_define import accredible_certification_created
from django.apps import apps
from django.db.models.signals import post_save, pre_delete

from relation.signals_define import user_certified

from ..signals.certification_deletion import certification_deletion_handler
from ..signals.certification_request import (
    certification_request_status_updated_handler,
    certification_request_post_save_handler,
    certification_request_issue_certification,
)
from ..signals_define import certification_request_payment_success, certification_request_status_updated
from .certification_payment import certification_request_payment_success_handler
from .certification_acquire import certification_request_acquired_handler
from .cohort import cohort_post_save_handler


def setup_signals():
    CertificationRequest = apps.get_model(
        app_label='exo_certification',
        model_name='CertificationRequest',
    )
    ConsultantRole = apps.get_model(
        app_label='relation',
        model_name='ConsultantRole',
    )
    CertificationCohort = apps.get_model(
        app_label='exo_certification',
        model_name='CertificationCohort',
    )

    certification_request_payment_success.connect(
        certification_request_payment_success_handler,
        sender=CertificationRequest)

    certification_request_status_updated.connect(
        certification_request_status_updated_handler,
        sender=CertificationRequest)

    post_save.connect(
        certification_request_post_save_handler,
        sender=CertificationRequest)

    user_certified.connect(
        certification_request_acquired_handler,
        sender=ConsultantRole)

    post_save.connect(
        cohort_post_save_handler,
        sender=CertificationCohort)

    pre_delete.connect(
        certification_deletion_handler,
        sender=CertificationRequest,
    )

    accredible_certification_created.connect(
        certification_request_issue_certification
    )
