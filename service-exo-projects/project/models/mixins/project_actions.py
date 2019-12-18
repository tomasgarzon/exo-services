from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q

from utils.permissions.objects import get_team_for_user


class ProjectActions:

    def users_without_team(self):
        q1 = Q(user_project_roles__project_role__project=self)
        COACH_OR_PARTICIPANT = [
            settings.EXO_ROLE_CODE_SPRINT_COACH,
            settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
        ]
        q2 = Q(
            user_project_roles__project_role__exo_role__code__in=COACH_OR_PARTICIPANT)
        q3 = Q(
            user_team_roles__team__project=self)
        return get_user_model().objects.filter(q1 & q2).exclude(q3)

    def user_actions(self, user_from):
        if self.created_by != user_from and not user_from.is_superuser:
            return []
        actions = [
            settings.PROJECT_CH_ACTION_EDIT,
            settings.PROJECT_CH_ACTION_DELETE]

        if self.is_draft:
            actions += settings.PROJECT_CH_ACTION_LAUNCH

        return actions

    def user_actions_for_user(self, user_from, user_to):
        action_edit_users = settings.PROJECT_CH_ACTION_EDIT in self.user_actions(user_from)
        if not action_edit_users:
            return []
        actions = [
            settings.PROJECT_CH_ACTION_USER_UNSELECT
        ]
        user_project_role = user_to.user_project_roles.first()
        if not user_project_role:
            return []
        is_participant_code = user_project_role.project_role.is_participant_code
        if is_participant_code:
            if not user_project_role.active:
                actions.append(settings.PROJECT_CH_ACTION_USER_EDIT_PARTICIPANT)
            else:
                actions.append(settings.PROJECT_CH_ACTION_USER_EDIT_TEAMS)
        else:
            actions.append(settings.PROJECT_CH_ACTION_USER_EDIT_ROLES)
        return actions

    def get_zone(self, user):
        if self.created_by == user:
            return settings.PROJECT_CH_ZONE_BACKOFFICE
        elif get_team_for_user(self, user).exists():
            return settings.PROJECT_CH_ZONE_PROJECT
        else:
            return settings.PROJECT_CH_ZONE_PROFILE
