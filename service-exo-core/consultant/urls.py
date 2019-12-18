from django.conf.urls import url

from .views.network import (
    list, crud,
    csv, html,
    bulk, bulk_list
)

app_name = 'consultant'

urlpatterns = [
    url(
        r'^list/$',
        list.NetworkListView.as_view(),
        name='list',
    ),
    url(
        r'^add/$',
        crud.ConsultantAdd.as_view(),
        name='add',
    ),
    url(
        r'^bulk-add/$',
        bulk.BulkCreationConsultantFormView.as_view(),
        name='bulk-add',
    ),
    url(
        r'^bulk-add-detail/(?P<pk>\d+)/$',
        bulk_list.BulkCreationConsultantDetailView.as_view(),
        name='bulk-add-detail',
    ),
    url(
        r'^bulk-list/$',
        bulk_list.BulkCreationListView.as_view(),
        name='bulk-list',
    ),
    url(
        r'^detail/(?P<pk>\d+)/$',
        crud.ConsultantDetailView.as_view(),
        name='detail',
    ),
    url(
        r'^disable/(?P<pk>\d+)/$',
        crud.ConsultantDisable.as_view(),
        name='disable',
    ),
    url(
        r'^export-csv/$',
        csv.ExportNetworkAsCSVView.as_view(),
        name='export-csv',
    ),
    url(
        r'^export-contracting-data/$',
        csv.ExportContractingDataAsCSVView.as_view(),
        name='export-contracting-csv',
    ),
    url(
        r'^export-certification/$',
        csv.ExportCertificationAsCSVView.as_view(),
        name='export-certification-csv',
    ),
    url(
        r'^export-bio-packages/$',
        html.ExportNetworkAsHTMLView.as_view(),
        name='export-bio-packages',
    ),
]
