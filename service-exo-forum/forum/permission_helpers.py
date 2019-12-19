from django.conf import settings
from circles.models import Circle

from actstream.models import Follow


def user_in_circle(user_from, circle):
    return user_from.is_superuser or\
        Follow.objects.following_qs(user_from, Circle).filter(
            object_id=circle.pk).exists()


def user_can_advise_project_questions(user_from):
    foundations_certified = False
    if user_from.is_consultant:
        foundations_certified = user_from.has_certified_role(
            settings.ROL_CH_EXO_FOUNDATIONS)
    return True if user_from.is_superuser or user_from.is_staff else foundations_certified


def user_in_team(user_from, team):
    project_perms = team.project.check_user_can_post(user_from)
    team_perms = team.check_user_can_post(user_from)
    return project_perms and team_perms


def user_in_qa_session(user_from, qa_session_team):
    return qa_session_team.session.advisors.filter(consultant__user=user_from).exists()
