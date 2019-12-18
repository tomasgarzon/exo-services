from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from .views import (
    project_status,
    service,
    project,
    certification
)

app_name = 'project'

router = DefaultRouter()
router.register(
    r'project', project.ProjectViewSet, basename='project')
router.register(
    r'backoffice', project.ProjectBackofficeViewSet,
    basename='project-backoffice')
router.register(
    r'admin-project',
    project.ProjectByUUIDViewSet,
    basename='project-admin')


urlpatterns = [
    url(
        r'join-level-1/$',
        certification.JoinUserCertificationLevel1.as_view(),
        name='join-certification-level-1-default',
    ),
    url(
        r'join-level-1/(?P<language>\w+)/$',
        certification.JoinUserCertificationLevel1.as_view(),
        name='join-certification-level-1',
    ),
    url(
        r'^create-service/$', service.ServiceCreateView.as_view(),
        name='create-service',
    ),
    url(
        r'^(?P<pk>\d+)/change-status/$',
        project_status.ProjectChangeStatusView.as_view(),
        name='change-status',
    ),
    url(
        r'^(?P<project_id>\d+)/team/',
        include('team.api.urls', namespace='team'),
    ),
    url(
        r'^(?P<project_id>\d+)/assignment/',
        include('assignment.api.urls', namespace='assignment'),
    ),
    url(
        r'^(?P<project_id>\d+)/team/(?P<team_id>\d+)/step/',
        include('project.api.urls_step', namespace='step'),
    ),
    url(r'^', include(router.urls)),
]
