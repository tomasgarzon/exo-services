from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.response import Response
from guardian.mixins import PermissionRequiredMixin

from utils.api.doc_mixin import APIObjectMixin

from ..serializers.image import ImageProfileSerializer
from ...conf import settings


class UpdateImageProfileView(
    PermissionRequiredMixin,
    APIObjectMixin,
    generics.UpdateAPIView
):
    """
    Use this endpoint to change user password.
    """
    permission_required = settings.EXO_ACCOUNTS_PERMS_USER_EDIT
    serializer_class = ImageProfileSerializer
    return_404 = True

    def get_queryset(self):
        return get_user_model().objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.profile_picture_origin = settings.EXO_ACCOUNTS_PROFILE_PICTURE_CH_USER
        instance.save(update_fields=['profile_picture_origin'])
        images = []
        for width, height in instance._meta.get_field('profile_picture').thumbnails:
            value = (
                (width, height),
                instance.profile_picture.get_thumbnail_url(width, height),
            )
            images.append(value)
        return Response(data=images, status=status.HTTP_200_OK)
