from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from ..serializers import ResourceCreateSerializer


class ResourceValidateURLView(APIView):
    """
    Validate public url for upload

    - URL: string (required)
    """

    http_method_names = ['post']
    serializer_class = ResourceCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        url = request.data.get('url')
        serializer = self.serializer_class()
        serializer.validate_url(data=url)
        return Response(True)
