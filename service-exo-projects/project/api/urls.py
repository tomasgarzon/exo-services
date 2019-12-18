from django.urls import path, include
from rest_framework_nested import routers

from team.api.views import team
from team.api.views import role as team_role

from .views import project, step, role, user_project_role, project_opportunities


app_name = 'api'

router = routers.SimpleRouter()


router.register(
    r'project',
    project.ProjectViewSet,
    basename='project',
)
router.register(
    r'project-opportunities',
    project_opportunities.ProjectOpportunityView,
    basename='project-opportunities')

nested_router = routers.NestedSimpleRouter(router, r'project', lookup='project')
nested_router.register(
    r'steps',
    step.StepViewSet, basename='project-step')
nested_router.register(
    r'roles',
    role.ProjectRoleViewSet, basename='project-role')
nested_router.register(
    r'team-roles',
    team_role.TeamRoleViewSet,
    basename='project-team-role')
nested_router.register(
    r'users',
    user_project_role.UsersViewSet,
    basename='project-user')
nested_router.register(
    r'exo-collaborators',
    user_project_role.ExOCollaboratorsViewSet,
    basename='project-exo-collaborator')
nested_router.register(
    r'participants',
    user_project_role.ParticipantsViewSet,
    basename='project-participant')
nested_router.register(
    r'teams',
    team.TeamViewSet, basename='project-team')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(nested_router.urls)),
]
