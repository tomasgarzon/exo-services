from django.conf.urls import url, include
from rest_framework import routers

from .views.consultant import trained, role

app_name = 'relation'

router_consultant = routers.DefaultRouter()
router_consultant.register(
    r'trained',
    trained.ConsultantTrainedViewSet,
    basename='consultant-trained',
)

router_consultant.register(
    r'roles',
    role.ConsultantRoleViewSet,
    basename='consultant-role',
)


urlpatterns = [
    url(
        r'^project/(?P<project_id>\d+)/',
        include('relation.api.urls_project', namespace='project'),
    ),
    url(
        r'^consultant/(?P<consultant_pk>\d+)/',
        include(router_consultant.urls),
    ),
]
