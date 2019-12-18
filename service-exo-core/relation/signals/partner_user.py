# SIGNALS between customer and user
from django.conf import settings


# instance has to be PartnerUserRole object
def when_user_partner_post_save(sender, instance, created, *args, **kwargs):
    update_fields = kwargs.get('update_fields') or []

    if (created and instance.is_active) or ('status' in update_fields):
        instance.partner.update_permissions(instance.user)

    if instance.is_active:
        instance.add_permission(settings.RELATION_CANCEL_ROLE, instance.user)
    else:
        instance.add_permission(settings.RELATION_ACTIVE_ROLE, instance.user)


# instance has to be PartnerUserRole object
def when_user_removed_to_partner(sender, instance, *args, **kwargs):
    instance.partner.update_permissions(instance.user)
