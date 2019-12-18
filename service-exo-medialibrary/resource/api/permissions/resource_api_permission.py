from django.contrib.auth.mixins import PermissionRequiredMixin

from rest_framework import permissions

from utils.permissions import has_library_perms


class ResourceAPIPermission(PermissionRequiredMixin, permissions.BasePermission):

    def has_permission(self, request, view):
        return has_library_perms(request.user)
