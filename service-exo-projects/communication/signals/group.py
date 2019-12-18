from django.conf import settings

from ..helper import (
    initialize_groups_for_project,
    create_team_group)
from ..tasks import (
    GroupCreateTask,
    GroupUpdateTask,
    GroupDeleteTask)


def project_launch_handler(sender, project, *args, **kwargs):
    initialize_groups_for_project(project, kwargs.get('user_from'))


def new_team_handler(sender, instance, created, *args, **kwargs):

    project = instance.project

    if created:
        if project.groups.exists():
            group = create_team_group(
                project, instance, project.created_by,
                create_conversation=False)
            GroupCreateTask().s(
                group_id=group.id,
                user_id=project.created_by.id).apply_async()
    else:
        if hasattr(instance, 'group'):
            GroupUpdateTask().s(
                group_id=instance.group.id,
                user_id=project.created_by.id).apply_async()


def delete_group_handler(sender, instance, *args, **kwargs):
    project = instance.project
    GroupDeleteTask().s(
        group_id=instance.id,
        user_id=project.created_by.id)


def delete_team_handler(sender, instance, *args, **kwargs):
    project = instance.project
    group = project.groups.filter(
        group_type=settings.COMMUNICATION_CH_TEAM,
        team__isnull=True).first()
    if group:
        group.delete()
