from ..tasks import GroupUpdateTask
from ..helper import update_group_for_user_in_project


def update_groups(project, user):
    groups = update_group_for_user_in_project(project, project.created_by, user)
    return
    for group_id in groups:
        if group_id is not None:
            GroupUpdateTask().s(
                group_id=group_id,
                user_id=project.created_by.id).apply_async()


def user_project_role_handler(sender, instance, created, *args, **kwargs):
    project = instance.project_role.project
    update_groups(project, instance.user)


def user_team_role_handler(sender, instance, created, *args, **kwargs):
    project = instance.team.project
    update_groups(project, instance.user)


def delete_project_role_handler(sender, instance, *args, **kwargs):
    project = instance.project_role.project
    update_groups(project, instance.user)


def delete_team_role_handler(sender, instance, *args, **kwargs):
    project = instance.team.project
    update_groups(project, instance.user)
