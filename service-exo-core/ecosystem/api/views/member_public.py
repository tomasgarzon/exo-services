from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from ecosystem.api.serializers.member import MemberPublicSerializer
from ecosystem.models import Member


class BasicPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'


class MemberPublicListAPIView(ListAPIView):
    permission_classes = (AllowAny, )
    pagination_class = BasicPageNumberPagination
    serializer_class = MemberPublicSerializer
    renderer_classes = (CamelCaseJSONRenderer, )
    queryset = Member.objects.filter_for_public().order_by('-modified')
    filter_backends = (filters.SearchFilter,)
    search_fields = (
        'user__full_name',
        'user__location',
        'user__consultant__consultant_roles__certification_role__name',
    )
