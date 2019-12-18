from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


class HttpResponseMixin:

    def gone_410_response(self, classname, object_id=None):
        response = Response(
            data={
                'classname': classname,
                'object_id': object_id},
            content_type="application/json",
            status=status.HTTP_410_GONE)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        return response
