from django.conf.urls import url  # noqa

from .views import certification_group

app_name = 'relation'

urlpatterns = [
    url(
        r'^list/$',
        certification_group.CertificationGroupListView.as_view(),
        name='group-list'),
    url(
        r'^create/$',
        certification_group.CertificationGroupCreateView.as_view(),
        name='group-create'),
    url(
        r'^update/(?P<pk>\d+)/$',
        certification_group.CertificationGroupUpdateView.as_view(),
        name='group-update'),
    url(
        r'^detail/(?P<pk>\d+)/$',
        certification_group.CertificationGroupDetailView.as_view(),
        name='group-detail'),
    url(
        r'^export/(?P<pk>\d+)/$',
        certification_group.CertificationGroupExportAsCSVView.as_view(),
        name='group-export-csv'),
]
