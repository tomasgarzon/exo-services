from django.conf import settings


def has_user_perms(user, perms):
    user_permissions = user.user_permissions.all().values_list("codename", flat=True)
    return set(perms).issubset(set(user_permissions))


def has_library_perms(user):
    return has_user_perms(user, settings.RESOURCE_ADMIN_PERMISSIONS) or user.is_superuser
