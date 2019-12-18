from django.urls import path, include
from rest_framework_nested import routers

from .views import view_project, view_step, view_user


app_name = 'api-view'

router = routers.SimpleRouter()


router.register(
    r'view-project',
    view_project.ProjectRetrieveViewSet,
    basename='project',
)
router.register(
    r'admin-project',
    view_project.ProjectRetrieveByUUIDViewSet,
    basename='project-admin')

nested_router = routers.NestedSimpleRouter(router, r'view-project', lookup='project')
nested_router.register(
    r'steps/(?P<team_pk>\d+)',
    view_step.StepViewSet, basename='project-step')
nested_router.register(
    r'users',
    view_user.UserViewSet, basename='project-user')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(nested_router.urls)),
    path(
        'files-versioned/',
        include('files.api.urls', namespace='files')),
]
