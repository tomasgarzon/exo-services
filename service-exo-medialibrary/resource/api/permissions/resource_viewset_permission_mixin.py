from rest_framework import viewsets

from utils.permissions import has_library_perms


class PermissionsModelViewSetMixin(viewsets.ModelViewSet):
    '''
    Mixed permission base model allowing for action level
    permission control. Subclasses may define their permissions
    by creating a 'permission_classes_by_action' variable.

    Example:
    permission_classes_by_action = {'list': [AllowAny],
                                    'create': [IsAdminUser]}
    '''

    permission_classes_by_action = {}

    def get_permissions(self):
        try:
            return [permission() for permission in self.get_permission_by_action()]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def get_permission_by_action(self):
        return self.permission_classes_by_action[self.action]

    def has_admin_perms(self):
        return has_library_perms(self.request.user)
