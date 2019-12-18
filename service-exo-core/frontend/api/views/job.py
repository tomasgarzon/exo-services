from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from utils.drf.permissions import ConsultantPermission

from ..serializers import job
from ...jobs.manager import manager as job_manager


class BasicPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class JobListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated, ConsultantPermission)
    serializer_class = job.JobSerializer
    pagination_class = BasicPageNumberPagination
    renderer_classes = (CamelCaseJSONRenderer, )

    def get_queryset(self):
        return job_manager.get_jobs(self.request.user)
