from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from ratings.models import Interaction
from relation.helpers.consultant_project_enum import ConsultantProjectEnum
from relation.models import ConsultantProjectRole


def update_consultant_project_role(role, user, overall_rating):
    ct = ContentType.objects.get_for_model(ConsultantProjectRole)
    interaction, _ = Interaction.objects.get_or_create(
        user=user,
        object_id=role.pk,
        content_type=ct)
    interaction.ratings.add(overall_rating)
    interaction.update()


def update_interaction_from_answer(answer, user):
    if not user.is_consultant:
        return None

    overall_rating = answer.ratings.first()

    if not overall_rating:
        return None

    role = answer.post.project.consultants_roles \
        .filter_by_exo_role_code(settings.EXO_ROLE_CODE_ADVISOR) \
        .filter_by_user(user) \
        .first()

    if role:
        update_consultant_project_role(role, user, overall_rating)


def update_interaction_from_team_step(team_step, consultant, relation_type):

    ct = ContentType.objects.get_for_model(consultant)
    overall_rating = team_step.ratings.filter(
        content_type=ct,
        object_id=consultant.pk
    ).first()

    if not overall_rating:
        return None

    if relation_type == ConsultantProjectEnum.COACH:
        role = consultant.roles \
            .filter_by_project(team_step.project) \
            .filter_by_exo_role_code(settings.EXO_ROLE_CODE_SPRINT_COACH) \
            .first()
    elif relation_type == ConsultantProjectEnum.HEAD:
        role = consultant.roles \
            .filter_by_project(team_step.project) \
            .filter_by_exo_role_code(settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH) \
            .first()
    if role:
        update_consultant_project_role(role, consultant.user, overall_rating)
