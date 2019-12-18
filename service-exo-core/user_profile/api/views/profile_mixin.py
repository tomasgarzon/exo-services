from django.contrib.auth import get_user_model

from rest_framework.generics import UpdateAPIView
from guardian.mixins import PermissionRequiredMixin

from utils.api.doc_mixin import APIObjectMixin

from ...conf import settings


class UpdateProfileMixin(
        PermissionRequiredMixin,
        APIObjectMixin,
        UpdateAPIView):

    permission_required = settings.EXO_ACCOUNTS_PERMS_USER_EDIT
    return_404 = True

    def get_queryset(self):
        return get_user_model().objects.all()
