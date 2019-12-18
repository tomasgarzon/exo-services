from exo_hub.helpers import add_permissions_by_hub, remove_permissions_by_hub
from exo_hub.models import ExOHub

from ..models import HubUser


def add_user_to_exo_hub_handler(sender, user, exo_hub_code, *args, **kwargs):
    try:
        exo_hub = ExOHub.objects.get(_type=exo_hub_code)
    except ExOHub.DoesNotExist:
        return
    hub_user, created = HubUser.objects.get_or_create(
        user=user, hub___type=exo_hub_code,
        defaults={
            'hub': exo_hub,
        })
    if created:
        add_permissions_by_hub(user=user, hub=exo_hub)


def remove_user_to_exo_hub_handler(sender, user, exo_hub_code, *args, **kwargs):
    try:
        hub_user = HubUser.objects.get(user=user, hub___type=exo_hub_code)
        remove_permissions_by_hub(user=user, hub=hub_user.hub)
        hub_user.delete()
    except HubUser.DoesNotExist:
        pass
