from django.conf.urls import url

from .views import performance

app_name = 'performance'

urlpatterns = [
    url(
        r'^sql/$',
        performance.PosgreSQLPerformanceView.as_view(),
        name='postgresql',
    ),
    url(
        r'^redis/$',
        performance.RedisPerformanceView.as_view(),
        name='redis',
    )
]
