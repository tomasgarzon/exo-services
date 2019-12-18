import django_filters

from django.contrib.auth.models import Permission

from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters import rest_framework as dj_filters

from exo_role.models import CertificationRole

from ..serializers.consultant import ConsultantSimpleSerializer
from ...models import Consultant


class ConsultantFilter(django_filters.FilterSet):
    permissions = django_filters.ModelMultipleChoiceFilter(
        field_name='user__user_permissions',
        lookup_expr='codename',
        to_field_name='codename',
        queryset=Permission.objects.all(),
    )
    certifications = django_filters.ModelMultipleChoiceFilter(
        field_name='consultant_roles__certification_role',
        lookup_expr='code',
        to_field_name='code',
        conjoined=True,
        queryset=CertificationRole.objects.all())

    class Meta:
        model = Consultant
        fields = ['permissions', 'certifications']


class ConsultantSearchViewSet(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    serializer_class = ConsultantSimpleSerializer
    model = Consultant

    filter_backends = (dj_filters.DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('user__short_name', 'user__full_name', 'user__email')
    filter_class = ConsultantFilter
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        page_size = self.request.GET.get('page_size')
        if page_size:
            queryset = queryset[:int(page_size)]
        return queryset

    def get_queryset(self):
        return self.model.objects.all()

    @action(detail=False, url_name='total-users', url_path='total-users')
    def total_users(self, request):
        queryset = self.model.objects.all()
        queryset = super().filter_queryset(queryset)
        return Response({'count': queryset.count()})
