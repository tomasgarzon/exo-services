from django.db.models import QuerySet
from django.conf import settings
from django.contrib.auth.models import Permission

from guardian.shortcuts import get_users_with_perms

from permissions.shortcuts import has_project_perms


class ProjectPermissions:

    def add_manager_permissions(self, user):
        # Add full access to Project
        self.add_permission(
            settings.PROJECT_PERMS_PROJECT_MANAGER,
            user,
        )

        # perms related object
        for attr_name, permissions in self.customize_manager.items():
            related_objects = []
            related_object = getattr(self, attr_name, None)
            if related_object:
                if not isinstance(related_object, QuerySet):
                    related_objects = [related_object]
                else:
                    related_objects = related_object
            for obj in related_objects:
                for perm in permissions:
                    obj.add_permission(perm, user)

        # User can access Customer List
        permission = Permission.objects.get(
            codename=settings.CUSTOMER_LIST_CUSTOMER,
        )
        user.user_permissions.add(permission)

    def remove_manager_permissions(self, user):
        # Remove full access to Project
        self.remove_permission(
            settings.PROJECT_PERMS_PROJECT_MANAGER,
            user,
        )

        # perms related object
        for attr_name, permissions in self.customize_manager.items():
            related_objects = []
            related_object = getattr(self, attr_name, None)
            if related_object:
                if not isinstance(related_object, QuerySet):
                    related_objects = [related_object]
                else:
                    related_objects = related_object
            for obj in related_objects:
                for perm in permissions:
                    obj.remove_permission(perm, user)

    def resfresh_manager_permissions_for_user(self, new_user, added=True):
        # call when a user has been added/removed from a service
        manager_list = [
            key for key, perms in get_users_with_perms(self, attach_perms=True).items()
            if settings.PROJECT_PERMS_PROJECT_MANAGER in perms
        ]

        for manager_user in manager_list:
            if manager_user == new_user:
                continue
            if added:
                new_user.add_permission(
                    settings.EXO_ACCOUNTS_PERMS_USER_EDIT,
                    manager_user)
            else:
                new_user.remove_permission(
                    settings.EXO_ACCOUNTS_PERMS_USER_EDIT,
                    manager_user)

    def has_perm(self, user, permission):
        return has_project_perms(self, permission, user)

    def check_user_can_post(self, user_from):
        return self.has_perm(user_from, settings.PROJECT_PERMS_VIEW_PROJECT)
