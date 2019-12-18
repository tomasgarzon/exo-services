from django.conf.urls import url

from .views import team, email

app_name = 'team'

urlpatterns = [
    url(
        r'^add/$',
        team.TeamCreateView.as_view(),
        name='create',
    ),
    url(
        r'^edit/(?P<pk>\d+)/$',
        team.TeamUpdateView.as_view(),
        name='edit',
    ),
    url(
        r'send-email/',
        email.SendMessageView.as_view(),
        name='send-email',
    ),
]
