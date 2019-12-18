from django.conf.urls import url, include
from rest_framework import routers

from .views.project import (
    consultant_role, user_role
)

app_name = 'relation'

router_badge = routers.DefaultRouter()
router_badge.register(
    r'roles',
    consultant_role.ConsultantProjectRoleViewSet,
    basename='consultantprojectrole',
)
router_badge.register(
    r'user_roles', user_role.UserProjectRoleViewSet,
    basename='userprojectrole',)


urlpatterns = [
    url(r'^', include(router_badge.urls)),
]
