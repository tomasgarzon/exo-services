from django.http import Http404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utils.authentication import UsernameAuthentication

from .resource_mixin import ResourceLibraryViewSetMixin
from ..serializers import ResourceListSerializer, ResourcePostSaveProjectSerializer
from ..filters.resource_filter import ResourceProjectFilter
from ..permissions import PermissionsModelViewSetMixin
from ...models import Resource


class ResourceLibraryProjectViewSet(PermissionsModelViewSetMixin, ResourceLibraryViewSetMixin):
    queryset = Resource.objects.all()
    http_method_names = ['get']
    filter_class = ResourceProjectFilter
    serializers = {
        'list': ResourceListSerializer,
    }
    permission_classes_by_action = {
        'list': [permissions.IsAuthenticated],
    }
    authentication_classes = (UsernameAuthentication, JSONWebTokenAuthentication)

    def get_queryset(self):
        if not self.request.GET.get('projects'):
            raise Http404

        return self.queryset.draft_and_available() if self.has_admin_perms() else self.queryset.available()


class ResourcePostSaveProjectView(APIView):
    http_method_names = ['post']
    serializer_class = ResourcePostSaveProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (UsernameAuthentication, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status.HTTP_200_OK)
