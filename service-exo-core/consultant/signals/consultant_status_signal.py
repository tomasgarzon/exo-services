from exo_accounts.signals_define import signal_username_created

from ..signals_define import (
    signal_update_consultant_status,
    consultant_post_activated,
    consultant_post_deactivated
)
from ..conf import settings


def update_consultant_status(sender, **kwargs):
    """
    Update the status of the Consultant depending of user status and
    Validations:
    """
    status = None
    consultant = kwargs.get('consultant')

    if not consultant.user.has_usable_password() and not consultant.get_pending_validations():
        status = settings.CONSULTANT_STATUS_CH_DISABLED
    elif consultant.validations.exclude(status=settings.CONSULTANT_VALIDATION_CH_ACCEPTED).count() == 0:
        status = settings.CONSULTANT_STATUS_CH_ACTIVE
    else:
        status = settings.CONSULTANT_STATUS_CH_PENDING_VALIDATION

    being_activated = consultant.status != status\
        and status == settings.CONSULTANT_STATUS_CH_ACTIVE
    being_deactivated = consultant.status != status \
        and status == settings.CONSULTANT_STATUS_CH_DISABLED

    if status != consultant.status:
        consultant.status = status
        consultant.save(update_fields=['status', 'modified'])

    # This consultant have been activated right now,
    #   so we have to generate the mailbox
    if being_activated:
        consultant.user.generate_public_username()
        signal_username_created.send(
            sender=sender,
            user=consultant.user,
        )
        consultant_post_activated.send(
            sender=consultant.__class__,
            consultant=consultant,
        )
    elif being_deactivated:
        consultant_post_deactivated.send(
            sender=sender,
            consultant=consultant,
        )


def post_save_user(sender, **kwargs):
    instance = kwargs.get('instance')
    if hasattr(instance, 'consultant'):
        signal_update_consultant_status.send(
            sender=None,
            consultant=instance.consultant,
        )
