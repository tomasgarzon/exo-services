from django.conf import settings

from exo_role.models import ExORole, CertificationRole

from .models import AdvisorRequestSettings, OpportunityTeamGroup
from .opportunities_helper import create_opportunity_group


def initialize_advisor_request_settings_for_project(project, user_from):
    project_type = {
        'fastracksprint': settings.EXO_ROLE_CODE_FASTRACK_ADVISOR,
        'genericproject': settings.EXO_ROLE_CODE_ADVISOR,
        'sprint': settings.EXO_ROLE_CODE_ADVISOR,
        'sprintautomated': settings.EXO_ROLE_CODE_ADVISOR,
        'workshop': settings.EXO_ROLE_CODE_ADVISOR}
    code_advisor = project_type.get(project.type_project_lower)
    if code_advisor is None:
        return
    return AdvisorRequestSettings.objects.create(
        project=project,
        total=0,
        exo_role=ExORole.objects.get(
            code=code_advisor),
        certification_required=CertificationRole.objects.get(
            code=settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS),
        entity=project.customer.__str__(),
        duration_unity=settings.OPPORTUNITIES_DURATION_UNITY_HOUR,
        duration_value=1,
        budgets=[],
    )


def create_team_group(project, team):
    try:
        advisor_request_settings = project.advisor_request_settings
    except AttributeError:
        return
    opportunity_group = OpportunityTeamGroup.objects.create(
        team=team)
    create_opportunity_group(
        advisor_request_settings,
        opportunity_group)
