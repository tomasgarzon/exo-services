from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Permission as DjangoPermission
from django.conf import settings


class UserAgreementMixin:

    def has_signed_marketplace_agreement(self):
        return self.has_perm(settings.EXO_ACCOUNTS_PERMS_MARKETPLACE_FULL_PERMISSION_REQUIRED)

    def sign_agreement(self, agreement):
        status = settings.AGREEMENT_USER_STATUS_SIGNED
        self.agreements.update_or_create(
            user=self,
            agreement=agreement,
            defaults={'status': status})

    def reject_agreement(self, agreement):
        status = settings.AGREEMENT_USER_STATUS_REVOKED
        self.agreements.update_or_create(
            user=self,
            agreement=agreement,
            defaults={'status': status})

    def add_django_permission(self, permission_name):
        permission = get_object_or_404(DjangoPermission, codename=permission_name)
        self.user_permissions.add(permission)

    def remove_django_permission(self, permission_name):
        permission = get_object_or_404(DjangoPermission, codename=permission_name)
        self.user_permissions.remove(permission)
