import logging

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission as DjangoPermission

from guardian.shortcuts import (
    assign_perm, remove_perm, get_perms_for_model,
    get_users_with_perms
)
from guardian.models import UserObjectPermission, Permission


logger = logging.getLogger('service')


class PermissionManagerMixin():
    """
        This mixin allows us to add or remove permissions using
        django-guardian app.
    """

    def add_permission(self, permission_name, user):
        try:
            assign_perm(permission_name, user, self)
        except DjangoPermission.DoesNotExist:
            logger.error('Permission does not exist: {}'.format(permission_name))

    def remove_permission(self, permission_name, user):
        try:
            remove_perm(permission_name, user, self)
        except DjangoPermission.DoesNotExist:
            logger.error('Permission does not exist: {}'.format(permission_name))

    def get_permissions(self):
        """
        Return a list of permissions related with this object
        """
        return get_perms_for_model(self)

    def get_user_perms(self, user):
        """
        Get the list of User permissions for this object
        """
        owner_content_type = ContentType.objects.get_for_model(self)
        user_perms = UserObjectPermission.objects.filter(
            user=user,
            content_type__pk=owner_content_type.pk,
            object_pk=self.id,
        ).values_list('permission_id', flat=True)
        permission_types = Permission.objects.filter(
            id__in=user_perms,
        ).values_list('codename', flat=True)
        return permission_types

    def get_granted_users(self, permissions=[]):
        """
        Return Users that are related with any kind of Permissions with
        this object
        """
        if not permissions:
            return get_users_with_perms(self)
        else:
            perms = get_users_with_perms(self, attach_perms=True)
            users = []
            for user, permission_list in perms.items():
                diff = set(permissions) - set(permission_list)
                if not diff:
                    users.append(user)
            return users

    def clear_user_perms(self, user):
        """
        Delete all perms associated with this user over this instance
        """
        user.clear_perms(self)
