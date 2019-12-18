from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from ratings.models import Interaction
from project.models import UserProjectRole
from team.rating_enum import ProjectEnum


def update_user_project_role(role, user, overall_rating):
    ct = ContentType.objects.get_for_model(UserProjectRole)
    interaction, _ = Interaction.objects.get_or_create(
        user=user,
        object_id=role.pk,
        content_type=ct)
    interaction.ratings.add(overall_rating)
    interaction.update()


def update_interaction_from_team_step(team_step, user, relation_type):
    ct = ContentType.objects.get_for_model(user)
    overall_rating = team_step.ratings.filter(
        content_type=ct,
        object_id=user.pk).first()
    if not overall_rating:
        return None

    role = None
    if relation_type == ProjectEnum.COACH:
        try:
            role = UserProjectRole.objects.get(
                project_role__project=team_step.project,
                user=user,
                project_role__code=settings.EXO_ROLE_CODE_SPRINT_COACH)
        except UserProjectRole.DoesNotExist:
            role = None
    elif relation_type == ProjectEnum.HEAD:
        try:
            role = UserProjectRole.objects.get(
                project_role__project=team_step.project,
                user=user,
                project_role__code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)
        except UserProjectRole.DoesNotExist:
            role = None
    if role:
        update_user_project_role(role, user, overall_rating)
