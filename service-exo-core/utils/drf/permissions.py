from rest_framework import permissions
from django.conf import settings


class ConsultantActivityPermission(permissions.BasePermission):
    permission_required = None

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        has_activity = request.user.has_perm(self.permission_required)
        return has_activity and request.user.is_consultant


class ConsultantAdvisingPermission(ConsultantActivityPermission):
    permission_required = settings.EXO_ACTIVITY_PERM_CH_ACTIVITY_ADVISING


class ConsultantConsultingPermission(ConsultantActivityPermission):
    permission_required = settings.EXO_ACTIVITY_PERM_CH_ACTIVITY_CONSULTING


class ConsultantPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return request.user.is_consultant


class MarketPlaceAgreementPermission(permissions.BasePermission):
    permission_required = settings.EXO_ACCOUNTS_PERMS_MARKETPLACE_FULL_PERMISSION_REQUIRED

    def has_permission(self, request, view):
        return request.user.has_perm(self.permission_required)
