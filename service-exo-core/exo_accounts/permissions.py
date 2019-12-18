from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from guardian.models import (
    UserObjectPermission,
    GroupObjectPermission,
    Permission,
)


class BaseUserPermission:

    # Clear all perms for get_perms_for_model(a customer
    def clear_perms(self, obj=None):
        if obj:
            obj_content_type = ContentType.objects.get_for_model(obj)
            q = Q(user=self,
                  content_type__pk=obj_content_type.pk,
                  object_pk=obj.id)
        else:
            q = Q(user=self)

        UserObjectPermission.objects.filter(q).delete()

        if not obj:
            GroupObjectPermission.objects.filter(
                group__id__in=self.groups.all().values_list('id', flat=True),
            ).delete()

    def get_perms(self, obj=None):
        """
        Get all permissions for the User
        """
        if obj:
            obj_content_type = ContentType.objects.get_for_model(obj)
            q = Q(user=self,
                  content_type__pk=obj_content_type.pk,
                  object_pk=obj.id)
        else:
            q = Q(user=self)

        user_perms = UserObjectPermission.objects.filter(q).values_list(
            'permission_id',
            flat=True,
        )
        permissions = Permission.objects.filter(id__in=user_perms).values_list(
            'codename',
            flat=True,
        )
        return list(permissions)

    def permissions(self):
        return list(self.user_permissions.values_list('codename', flat=True))
