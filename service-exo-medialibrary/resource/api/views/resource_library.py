from django.http import Http404

from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utils.authentication import UsernameAuthentication

from .resource_mixin import ResourceLibraryViewSetMixin
from ..serializers import (
    ResourceListSerializer, ResourceCreateSerializer,
    ResourceUpdateSerializer, ResourceAddProjectSerializer,
    ResourceRemoveProjectSerializer)
from ..filters.resource_filter import ResourceFilter
from ..permissions import ResourceAPIPermission, PermissionsModelViewSetMixin
from ...models import Resource


class ResourceLibraryViewSet(PermissionsModelViewSetMixin, ResourceLibraryViewSetMixin):
    queryset = Resource.objects.all()
    http_method_names = ['get', 'post', 'put', 'delete']
    filter_class = ResourceFilter
    serializers = {
        'list': ResourceListSerializer,
        'create': ResourceCreateSerializer,
        'update': ResourceUpdateSerializer,
        'add_to_projects': ResourceAddProjectSerializer,
        'remove_from_projects': ResourceRemoveProjectSerializer,
    }
    permission_classes_by_action = {
        'list': [permissions.IsAuthenticated],
        'create': [ResourceAPIPermission],
        'update': [ResourceAPIPermission],
        'destroy': [ResourceAPIPermission]
    }
    authentication_classes = (UsernameAuthentication, JSONWebTokenAuthentication)

    def get_queryset(self):
        if self.action == 'list':
            if not self.request.GET.get('sections') and not self.request.user.is_superuser:
                raise Http404
            elif self.request.GET.get('sections') == ',':
                raise Http404

        return self.queryset.draft_and_available() if self.has_admin_perms() else self.queryset.available()

    @action(detail=True, methods=['put'], url_path='add-to-projects')
    def add_to_projects(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='remove-from-projects')
    def remove_from_projects(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
