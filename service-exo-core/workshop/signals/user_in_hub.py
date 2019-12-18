from django.conf import settings
from django.contrib.auth.models import Permission

from exo_hub.models import ExOHub


def get_exo_hub(exo_hub_code):
    try:
        return ExOHub.objects.get(_type=exo_hub_code)
    except ExOHub.DoesNotExist:
        return None


def add_user_in_hub_handler(sender, user, exo_hub_code, *args, **kwargs):
    hub = get_exo_hub(exo_hub_code)
    if hub and hub.is_trainer:
        perm = Permission.objects.get(
            codename=settings.WORKSHOP_PERMS_ADD_WORKSHOP)
        user.user_permissions.add(perm)


def remove_user_in_hub_handler(sender, user, exo_hub_code, *args, **kwargs):
    hub = get_exo_hub(exo_hub_code)
    if hub and hub.is_trainer:
        perm = Permission.objects.get(
            codename=settings.WORKSHOP_PERMS_ADD_WORKSHOP)
        user.user_permissions.remove(perm)
