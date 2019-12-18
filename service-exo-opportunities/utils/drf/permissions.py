from django.conf import settings

from rest_framework import permissions


class MarketPlaceAgreementPermission(permissions.BasePermission):
    permission_required = settings.AUTH_USER_PERMS_MARKETPLACE_FULL_PERMISSION_REQUIRED

    def has_permission(self, request, view):
        return request.user.has_perm(self.permission_required)
