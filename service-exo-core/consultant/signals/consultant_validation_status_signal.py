from ..signals_define import signal_update_consultant_status


def post_save_consultant_validation_status(sender, **kwargs):

    consultant_validation = kwargs.get('instance')

    signal_update_consultant_status.send(
        sender=None,
        consultant=consultant_validation.consultant,
    )
