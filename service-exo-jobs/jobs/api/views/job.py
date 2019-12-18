from rest_framework import mixins, viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from utils.drf.authentication import UsernameAuthentication

from ..serializers.job import JobSerializer
from ..serializers.admin import JobCreateSerializer
from ...models import Job


class JobViewSet(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    serializer_class = JobSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering = ['status_order', 'end']
    search_fields = ['title']

    def get_queryset(self):
        return self.request.user.jobs.all().annotate_status_order()


class AdminJobViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    model = Job
    serializer_class = JobCreateSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (UsernameAuthentication, )
    filter_backends = [DjangoFilterBackend]
    lookup_field = 'uuid'
    filterset_fields = ['related_uuid', 'related_class', 'user__uuid']

    def get_queryset(self):
        return self.model.objects.all()
