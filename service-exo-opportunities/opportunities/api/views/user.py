from django.contrib.auth import get_user_model
import django
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from utils.drf.authentication import UsernameAuthentication

from ..serializers.user import (
    UserUUIDSerializer,
    UserUUIDAddPermSerializer,
    UserUUIDRemovePermSerializer)


class UserUUIDViewSet(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = get_user_model().objects.all()
    authentication_classes = (UsernameAuthentication, )
    renderer_classes = (CamelCaseJSONRenderer, )
    permission_classes = (IsAuthenticated,)
    lookup_field = 'uuid'

    serializers = {
        'default': UserUUIDSerializer,
        'retrieve': UserUUIDSerializer,
        'add_permission': UserUUIDAddPermSerializer,
        'remove_permission': UserUUIDRemovePermSerializer,
    }

    def get_object(self, *args, **kwargs):
        try:
            return super().get_object(*args, **kwargs)
        except django.http.response.Http404:
            user, _ = get_user_model().objects.get_or_create(
                uuid=self.kwargs.get('uuid'))
            return user

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    @action(detail=True, methods=['post'], url_path='add-permission')
    def add_permission(self, request, uuid):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='remove-permission')
    def remove_permission(self, request, uuid):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
