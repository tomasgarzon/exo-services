from django.http import Http404
from django.utils.text import slugify

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import parsers

from utils.files import split_filename

from ...storage.base import resource_storage
from ..serializers.resource import ResourceRelatedSerializer, ResourceSerializer
from ...models import Resource


class ResourceStorageMixin():

    def store_file(self, file):
        storage = resource_storage.build()
        [original_name, extension] = split_filename(file.name)
        file_name = '{}{}'.format(slugify(original_name), extension)
        new_file_name = storage.save(name=file_name, content=file)
        return {
            'name': original_name,
            'extension': extension.replace('.', ''),
            '_filename': new_file_name,
            'file_size': file.size,
            'mimetype': file.content_type,
        }


class ResourceUploadView(ResourceStorageMixin, APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        file = request.FILES.get('file', None)
        if not file:
            raise Http404
        data = self.store_file(file)
        return Response(data)


class UserResourceUploadView(ResourceStorageMixin, APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ResourceRelatedSerializer
    parser_classes = (parsers.MultiPartParser, )

    def post(self, request, format=None):
        file = request.FILES.get('file', None)
        link = request.data.get('link', None)
        if not file and not link:
            raise Http404
        serializer = ResourceRelatedSerializer(data=request.data)
        if serializer.is_valid():
            if file:
                data = self.store_file(file)
            else:
                link = request.data.get('link')
                if not link.startswith('http://') and not link.startswith('https://'):
                    link = 'http://' + link
                data = {
                    'name': request.data.get('name'),
                    'link': link,
                }
            content_type = serializer.validated_data.get('content_type')
            object_id = serializer.validated_data.get('object_id')
            team = serializer.validated_data.get('team')
            object_related = content_type.get_object_for_this_type(pk=object_id)
            resource = Resource.objects.create_user_resource(
                user_from=request.user,
                team=team,
                related=object_related,
                **data
            )
            serializer = ResourceSerializer(resource)
            return Response(serializer.data)
        return Response(data)
