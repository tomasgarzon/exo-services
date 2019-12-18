from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from utils.drf.permissions import ConsultantPermission

from ...models import Member
from ...conf import EcosystemConfig
from ..serializers.member import MemberSerializer


class BasicPageNumberPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'


class MemberListAPIView(ListAPIView):
    pagination_class = BasicPageNumberPagination
    permission_classes = (IsAuthenticated, ConsultantPermission)
    serializer_class = MemberSerializer
    renderer_classes = (CamelCaseJSONRenderer, )
    queryset = Member.objects.filter(user__consultant__isnull=False)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user__full_name', 'user__location', 'user__consultant__exo_profile__personal_mtp')

    def get_ordering(self):
        order_param = self.request.query_params.get('sort', None)
        direction = 1
        ordering_dict = {
            'name': 'user__full_name',
            'registered': 'user__date_joined',
            'location': 'user__location',
            'projects': 'num_projects',
            'activity': 'modified',
            'status': 'user__consultant__status',
        }
        default_ordering = '-{}'.format(ordering_dict.get('activity'))

        ordering = default_ordering

        if order_param:
            if order_param[0] == '-':
                direction = -1
                order_param = order_param[1:]

            if order_param in ordering_dict.keys():
                ordering = ordering_dict.get(order_param)

        if ordering == 'status' and not self.request.user.is_admin:
            ordering = default_ordering

        if ordering != default_ordering and direction < 0:
            ordering = '-{}'.format(ordering)

        return ordering

    def get_initial_queryset_by_status(self):
        user = self.request.user
        filter_status = self.request.query_params.get('status', None)

        if user.is_admin and filter_status:
            if filter_status == EcosystemConfig.API_STATUS_ALL:
                query = self.queryset
            elif filter_status == EcosystemConfig.API_STATUS_INACTIVE:
                query = self.queryset.filter_inactive()
            else:
                query = self.queryset.filter_active()
        else:
            query = self.queryset.filter_active()

        return query

    def get_queryset(self):
        query = self.get_initial_queryset_by_status()
        available_filters = [
            'industries',
            'attributes',
            'certifications',
            'roles',
            'activities',
            'technologies',
            'languages',
            'location',
        ]

        for f in available_filters:
            value = self.request.GET.get(f, None)
            if value:
                query = getattr(query, 'filter_by_{}'.format(f))(value.split(','))

        return query.order_by(self.get_ordering())
