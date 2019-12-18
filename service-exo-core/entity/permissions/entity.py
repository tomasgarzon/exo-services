from permissions.models import PermissionManagerMixin


class EntityPermissionMixin(PermissionManagerMixin):

    def add_admin_permission(self, user):
        ADMIN_PERMISSIONS = self._meta_permissions.permissions_admin
        for permission_name in ADMIN_PERMISSIONS:
            self.add_permission(permission_name, user)
        self.add_regular_permission(user)

    def remove_admin_permission(self, user):
        ADMIN_PERMISSIONS = self._meta_permissions.permissions_admin
        for permission_name in ADMIN_PERMISSIONS:
            self.remove_permission(permission_name, user)

    def add_regular_permission(self, user):
        REGULAR_PERMISSIONS = self._meta_permissions.permissions_regular
        for permission_name in REGULAR_PERMISSIONS:
            self.add_permission(permission_name, user)

    def remove_regular_permission(self, user):
        REGULAR_PERMISSIONS = self._meta_permissions.permissions_regular
        for permission_name in REGULAR_PERMISSIONS:
            self.remove_permission(permission_name, user)

    def update_permissions(self, user):
        is_admin = self.users_roles.actives().filter_by_user(user).has_admin_role()
        if is_admin:
            self.add_admin_permission(user)
        else:
            self.remove_admin_permission(user)
            is_regular = self.users_roles.actives().filter_by_user(user).has_regular_role()
            if is_regular:
                self.add_regular_permission(user)
            else:
                self.remove_regular_permission(user)
