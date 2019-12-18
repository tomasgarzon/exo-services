from rest_framework import permissions


class IsConsultantOwnerOrAdmin(permissions.IsAdminUser):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        return super(IsConsultantOwnerOrAdmin, self).has_object_permission(
            request, view, obj,
        ) and (obj.owner == request.user or request.user.is_admin)

    def has_permission(self, request, view):

        return super(
            IsConsultantOwnerOrAdmin,
            self,
        ).has_permission(request, view) or hasattr(request.user, 'consultant')
