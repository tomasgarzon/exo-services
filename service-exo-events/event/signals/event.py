from django.conf import settings

from guardian.shortcuts import assign_perm

from certification.signals_define import (
    create_certification_group,
    delete_certification_group,
    update_certification_group)

from utils.certification_helpers import CertificationWorkshopWrapper

from ..tasks import CreateWorkshopWebsiteTask, DeleteWorkshopWebsiteTask


def post_save_event(sender, instance, created, *args, **kwargs):
    system_enabled = not settings.POPULATOR_MODE and settings.ACCREDIBLE_ENABLED
    instance_enabled = created and instance.is_openexo_workshop

    if created:
        assign_perm(
            settings.EVENT_PERMS_EDIT_EVENT,
            instance.created_by,
            instance,
        )

    if instance_enabled and not settings.POPULATOR_MODE:
        if settings.ACCREDIBLE_ENABLED:
            event_wrapper = CertificationWorkshopWrapper(instance)
            event_wrapper_data = event_wrapper.get_data(instance.created_by)
            create_certification_group.send(sender=instance.__class__, **event_wrapper_data)

        CreateWorkshopWebsiteTask().s(
            uuid=instance.uuid,
            slug=instance.slug,
            user_from=instance.created_by.pk,
        ).apply_async()

    elif system_enabled and instance.credentials.exists():
        certification_group = instance.credentials.first()
        update_certification_group.send(
            sender=instance.__class__,
            instance=certification_group,
            user_from=instance.created_by,
            group_name='{name} - {location}'.format(
                name=instance.title,
                location=instance.location_for_certification),
            description=instance.description_for_certification,
            course_name=instance.title,
            issued_on=instance.start)


def pre_delete_event(sender, instance, *args, **kwargs):
    if not settings.POPULATOR_MODE:
        if settings.ACCREDIBLE_ENABLED:
            delete_certification_group.send(
                sender=instance.__class__, instance=instance)
        DeleteWorkshopWebsiteTask().s(
            uuid=instance.uuid, user_from=instance.created_by.pk
        ).apply_async()
