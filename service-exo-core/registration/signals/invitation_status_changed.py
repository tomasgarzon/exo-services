# SIGNALS between customer and user
from django.contrib.contenttypes.models import ContentType

from ..models import RegistrationProcess


def when_invitation_registration_post_save(sender, instance, created, *args, **kwargs):
    if not created:
        update_fields = kwargs.get('update_fields') or []
        if 'status' in update_fields:
            if (instance.is_active or instance.is_cancelled) and \
                    instance.has_registration is not None:
                validation_obj = instance.validation_object
                object_id = validation_obj.id
                content_type_id = ContentType.objects.get_for_model(validation_obj).id
                processes = RegistrationProcess.objects.filter_by_content_object(
                    object_id,
                    content_type_id,
                )
                for process in processes:
                    code = process.current_step.code
                    if instance.is_active:
                        process.execute_step(process.user_from, code)
                    else:
                        process.cancel_step(
                            process.user_from,
                            code,
                            description=instance.description_response,
                        )
