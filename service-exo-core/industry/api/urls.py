from django.conf.urls import url

from .views import (
    IndustryAPIView,
    IndustryListAPIView,
    IndustrySelect2
)

urlpatterns = [
    url(
        r'^$',
        IndustryAPIView.as_view(),
        name='industries',
    ),

    url(
        r'^list/select2/$',
        IndustrySelect2.as_view(),
        name='industries-select2',
    ),

    url(
        r'^list/$', IndustryListAPIView.as_view(),
        name='industries-list',
    ),
]
