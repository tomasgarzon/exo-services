from django.conf import settings

from exo_role.models import ExORole, CertificationRole

from .models import AdvisorRequestSettings, OpportunityTeamGroup
from .opportunities_helper import create_opportunity_group


def initialize_advisor_request_settings_for_project(project, user_from):
    return AdvisorRequestSettings.objects.create(
        project=project,
        total=0,
        exo_role=ExORole.objects.get(
            code=settings.EXO_ROLE_CODE_ADVISOR),
        certification_required=CertificationRole.objects.get(
            code=settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS),
        entity=project.customer,
        duration_unity=settings.OPPORTUNITIES_DURATION_UNITY_HOUR,
        duration_value=1,
        budgets=[],
    )


def create_team_group(project, team):
    advisor_request_settings = project.advisor_request_settings
    opportunity_group = OpportunityTeamGroup.objects.create(
        team=team)
    create_opportunity_group(
        advisor_request_settings,
        opportunity_group)
