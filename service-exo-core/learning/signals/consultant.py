from django.contrib.auth.models import Permission

from ..conf import settings


def consultant_post_save_resource_perms(sender, instance, created, *args, **kwargs):
    if created:
        permission = Permission.objects.get(
            codename=settings.LEARNING_LIST_RESOURCE_PERMS,
        )
        instance.user.user_permissions.add(permission)
