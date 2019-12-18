from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Group


User = get_user_model()


def _create_group(project, user_from, group_category, role_category, create_conversation=True):
    group = Group.objects.create(
        group_type=group_category,
        project=project,
        created_by=user_from)
    users = User.objects.filter(
        user_project_roles__project_role__project=project,
        user_project_roles__project_role__groups__icontains=role_category)
    group.users.add(*users)
    if create_conversation:
        group.create(user_from)
    return group


def create_general_group(project, user_from, create_conversation=True):
    return _create_group(
        project, user_from,
        settings.COMMUNICATION_CH_GENERAL,
        settings.PROJECT_CH_GROUP_GENERAL,
        create_conversation)


def create_collaborators_group(project, user_from, create_conversation=True):
    return _create_group(
        project, user_from,
        settings.COMMUNICATION_CH_COLLABORATORS,
        settings.PROJECT_CH_GROUP_COLLABORATORS,
        create_conversation)


def _users_for_team(project, team):
    users = []
    TEAMS = settings.PROJECT_CH_GROUP_TEAMS
    TEAM = settings.PROJECT_CH_GROUP_TEAM
    team_users = User.objects.filter(
        user_project_roles__project_role__project=project,
        user_project_roles__project_role__groups__icontains=TEAMS)
    users.extend(list(team_users))

    team_users = User.objects.filter(
        user_project_roles__project_role__project=project,
        user_project_roles__project_role__groups__icontains=TEAM,
        user_team_roles__team=team)
    users.extend(list(team_users))
    return users


def create_team_group(project, team, user_from, create_conversation=True):
    group = Group.objects.create(
        group_type=settings.COMMUNICATION_CH_TEAM,
        project=project,
        team=team,
        created_by=user_from)

    users = _users_for_team(project, team)
    group.users.add(*users)
    if create_conversation:
        group.create(user_from)
    return group


def initialize_groups_for_project(project, user_from):
    create_general_group(project, user_from)
    create_collaborators_group(project, user_from)
    for team in project.teams.all():
        create_team_group(project, team, user_from)


def update_group(project, group_category, role_category):
    group = project.groups.filter(
        group_type=group_category).first()
    if not group:
        return

    users = User.objects.filter(
        user_project_roles__project_role__project=project,
        user_project_roles__project_role__groups__icontains=role_category)
    group.users.clear()
    group.users.add(*users)


def update_general_group(project):
    update_group(
        project,
        settings.COMMUNICATION_CH_GENERAL,
        settings.PROJECT_CH_GROUP_GENERAL)


def update_collaborators_group(project):
    update_group(
        project,
        settings.COMMUNICATION_CH_COLLABORATORS,
        settings.PROJECT_CH_GROUP_COLLABORATORS)


def update_team_group(project, team):
    if not hasattr(team, 'group'):
        return
    group = team.group
    users = _users_for_team(project, team)
    group.users.clear()
    group.users.add(*users)


def update_group_for_user_in_project(project, user_from, user):
    actual_groups = user.communication_groups.filter(
        project=project).values_list('id', flat=True)
    update_general_group(project)
    update_collaborators_group(project)
    for team in project.teams.all():
        update_team_group(project, team)
    new_groups = user.communication_groups.filter(
        project=project).values_list('id', flat=True)
    groups_added = set(new_groups) - set(actual_groups)
    groups_removed = set(actual_groups) - set(new_groups)
    return groups_added.union(groups_removed)
