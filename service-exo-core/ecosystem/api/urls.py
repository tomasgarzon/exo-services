from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views.member import MemberListAPIView
from .views.filters import EcosystemFiltersAPIView

app_name = 'ecosystem'

urlpatterns = [
    url(
        r'^members/$',
        MemberListAPIView.as_view(),
        name='members',
    ),
    url(
        r'^filters/$',
        EcosystemFiltersAPIView.as_view(),
        name='filters',
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
