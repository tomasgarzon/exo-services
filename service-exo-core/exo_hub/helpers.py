from django.conf import settings
from django.contrib.auth.models import Permission


PERMISSIONS_BY_HUB = {
    settings.EXO_HUB_CH_CONSULTANT: [
        settings.EXO_ACCOUNTS_PERMS_ACCESS_EXQ,
    ],
    settings.EXO_HUB_CH_COACH: [],
    settings.EXO_HUB_CH_ALUMNI: [],
    settings.EXO_HUB_CH_AMBASSADORS: [],
    settings.EXO_HUB_CH_TRAINER: [],
    settings.EXO_HUB_CH_INVESTOR: [],
}


def add_permissions_by_hub(user, hub):
    for permission in PERMISSIONS_BY_HUB.get(hub._type, []):
        perm = Permission.objects.get(codename=permission)
        user.user_permissions.add(perm)


def remove_permissions_by_hub(user, hub):
    for permission in PERMISSIONS_BY_HUB.get(hub._type, []):
        perm = Permission.objects.get(codename=permission)
        user.user_permissions.remove(perm)
