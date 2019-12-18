from django.conf.urls import url

from .views.team import team_list, team_crud


app_name = 'team'

urlpatterns = [
    # TEAM SECTION
    url(
        r'^list/$',
        team_list.TeamListView.as_view(),
        name='list',
    ),
    url(
        r'^add/$',
        team_crud.TeamCreateView.as_view(),
        name='add',
    ),
    url(
        r'^detail/(?P<pk>\d+)/$',
        team_crud.TeamDetailView.as_view(),
        name='detail',
    ),
    url(
        r'^edit/(?P<pk>\d+)/$',
        team_crud.TeamEditView.as_view(),
        name='edit',
    ),
    url(
        r'^delete/(?P<pk>\d+)/$',
        team_crud.TeamDeleteView.as_view(),
        name='delete',
    ),
]
