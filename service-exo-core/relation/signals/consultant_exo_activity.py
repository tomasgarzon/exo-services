

def activate_exo_activity_with_no_agreement(
    sender, instance, created,
    *args, **kwargs
):
    if created:
        instance.enable()


def activate_deactivate_consultant_exo_activity_status(
    sender, instance,
    created, *args, **kwargs
):
    if instance.is_enabled:
        instance.add_permissions_related_to_activity()
    elif instance.is_disabled:
        instance.remove_permissions_related_to_activity()
