from django.contrib.auth import get_user_model
from django.http import Http404

from rest_framework import viewsets, mixins
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny

from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from ..serializers.profile_public import ProfilePublicSerializer, ProfilePublicOwnUser


class UserProfilePublicView(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = ProfilePublicSerializer
    renderer_classes = (CamelCaseJSONRenderer, JSONRenderer,)
    permission_classes = (AllowAny,)
    lookup_field = 'slug'

    def get_queryset(self):
        try:
            user = get_user_model().objects.get(slug=self.kwargs.get('slug'))
        except get_user_model().DoesNotExist:
            raise Http404
        user_is_not_active_consultant = user.is_consultant and not user.consultant.is_active
        user_not_see_itself = user != self.request.user

        if user_is_not_active_consultant and user_not_see_itself:
            raise Http404
        return self.queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == request.user:
            self.serializer_class = ProfilePublicOwnUser
        return super().retrieve(request, args, kwargs)
