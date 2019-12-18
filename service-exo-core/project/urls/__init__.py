from django.conf.urls import url, include

from ..views import (
    project_list, project_crud
)

app_name = 'project'

urlpatterns = [
    url(
        r'^services/list/$',
        project_list.ProjectListView.as_view(),
        name='service-list',
    ),
    url(
        r'^detail/(?P<pk>\d+)/$',
        project_crud.ProjectDetailView.as_view(),
        name='project-detail',
    ),
    url(
        r'^export-participant/(?P<pk>\d+)/$',
        project_crud.ProjectExportAsCSVView.as_view(),
        name='export-participant',
    ),
    url(
        r'^delete/(?P<pk>\d+)/$',
        project_crud.ProjectDeleteView.as_view(),
        name='delete',
    ),
    # ZONE
    url(
        r'^(?P<project_id>\d+)/',
        include('project.urls.url_zone', namespace='project'),
    ),
]
