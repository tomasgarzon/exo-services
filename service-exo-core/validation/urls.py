from django.conf.urls import url

from .views import list as validation_list
from .views import actions

app_name = 'validations'

urlpatterns = [
    url(
        r'^list/$',
        validation_list.ValidationListView.as_view(),
        name='list',
    ),
    url(
        r'^run/$',
        actions.RunValidationView.as_view(),
        name='run',
    ),
]
