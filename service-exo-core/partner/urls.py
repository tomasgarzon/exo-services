from django.conf.urls import url

from .views import (
    partner_list, partner_crud
)

app_name = 'partner'

urlpatterns = [
    url(
        r'^list/$',
        partner_list.PartnerListView.as_view(),
        name='list',
    ),
    url(
        r'^add/$',
        partner_crud.PartnerCreateView.as_view(),
        name='add',
    ),
    url(
        r'^edit/(?P<pk>\d+)/$',
        partner_crud.PartnerEditView.as_view(),
        name='edit',
    ),
    url(
        r'^detail/(?P<pk>\d+)/$',
        partner_crud.PartnerDetailView.as_view(),
        name='detail',
    ),
    url(
        r'^delete/(?P<pk>\d+)/$',
        partner_crud.PartnerDeleteView.as_view(),
        name='delete',
    ),
]
