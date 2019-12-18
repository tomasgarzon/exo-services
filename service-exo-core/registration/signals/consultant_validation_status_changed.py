from ..models import RegistrationProcess


def _register_registration_process_change(
        registration_process,
        message,
        status,
        display_status,
        related_object=None,
):

    registration_process._store_log(
        text=message,
        status=status,
        display_status=display_status,
        related_object=related_object,
    )


def when_consultant_validation_status_update(
    sender, instance, created,
    *args, **kwargs
):
    """
    This signal will control the Registration process email events to update
    the corresponding Log for the customer
    """
    if not created:
        update_fields = kwargs.get('update_fields') or []

        if 'status' in update_fields:
            try:
                registration_process = instance.consultant.user.registration_process
                message = '{}'.format(instance.validation_type_display)
                _register_registration_process_change(
                    registration_process,
                    message,
                    instance.status,
                    instance.get_status_display().lower(),
                    instance,
                )
            except RegistrationProcess.DoesNotExist:
                """
                The ConsultantValidation doesn't have to include a \
                RegistrationProcess
                """
                pass
