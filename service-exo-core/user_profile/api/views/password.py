from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash

from rest_framework import generics, status
from rest_framework.response import Response
from guardian.mixins import PermissionRequiredMixin

from utils.api.doc_mixin import APIObjectMixin

from ..serializers.password import PasswordRetypeSerializer
from ...conf import settings


class SetPasswordView(
    PermissionRequiredMixin,
    APIObjectMixin,
    generics.UpdateAPIView
):
    """
    Use this endpoint to change user password.
    """
    permission_required = settings.EXO_ACCOUNTS_PERMS_USER_EDIT
    serializer_class = PasswordRetypeSerializer
    return_404 = True

    def get_queryset(self):
        return get_user_model().objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(data={}, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        user = self.get_object()
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        update_session_auth_hash(self.request, user)
        return user
