from django.conf import settings

from project.models import Project

from .models import ExOHub


def clear_exo_hub_alumni():
    hub = ExOHub.objects.get(_type=settings.EXO_HUB_CH_ALUMNI)
    for user in hub.users.all():
        user.delete()


def add_coaches_and_head_coach_as_alumni():
    hub = ExOHub.objects.get(_type=settings.EXO_HUB_CH_ALUMNI)
    consultants = []
    for project in Project.objects.filter(category=settings.PROJECT_CH_CATEGORY_TRANSFORMATION):
        consultants += list(project.consultants_roles.filter_by_exo_role_code(
            settings.EXO_ROLE_CODE_SPRINT_COACH).consultants())
        consultants += list(project.consultants_roles.filter_by_exo_role_code(
            settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH).consultants())

    for consultant in set(consultants):
        hub.users.get_or_create(user=consultant.user)
