
from rest_framework import generics, viewsets
from rest_framework import permissions

from ..serializers.service_request import ServiceRequestSerializer
from ...models import ServiceRequest


class ServiceRequestViewSet(generics.ListAPIView, viewsets.ModelViewSet):
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['post']
