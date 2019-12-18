from django.conf import settings

from ..models import ExOHub


def consultant_to_hub_handler(sender, consultant, *args, **kwargs):
    is_participant = consultant.user.projects_member \
        .filter_by_exo_role_code(settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT) \
        .filter(project__category=settings.PROJECT_CH_CATEGORY_TRANSFORMATION) \
        .exists()

    if is_participant:
        hub = ExOHub.objects.get(_type=settings.EXO_HUB_CH_ALUMNI)
        hub.users.get_or_create(user=consultant.user)
