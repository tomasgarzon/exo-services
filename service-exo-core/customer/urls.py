from django.conf.urls import url

from .views import (
    customer_list, customer_crud
)


app_name = 'customer'

urlpatterns = [
    url(
        r'^list/$',
        customer_list.CustomerListView.as_view(),
        name='list',
    ),
    url(
        r'^add/$',
        customer_crud.CustomerCreateView.as_view(),
        name='add',
    ),
    url(
        r'^edit/(?P<pk>\d+)/$',
        customer_crud.CustomerEditView.as_view(),
        name='edit',
    ),
    url(
        r'^detail/(?P<pk>\d+)/$',
        customer_crud.CustomerDetailView.as_view(),
        name='detail',
    ),
    url(
        r'^delete/(?P<pk>\d+)/$',
        customer_crud.CustomerDeleteView.as_view(),
        name='delete',
    ),
]
