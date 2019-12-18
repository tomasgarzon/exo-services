from ..helper import (
    initialize_advisor_request_settings_for_project,
    create_team_group)
from ..tasks import (
    OpportunityGroupUpdateTask,
    OpportunityGroupCreateTask,
    OpportunityGroupDeleteTask)


def project_launch_handler(sender, project, *args, **kwargs):
    try:
        advisor_settings = project.advisor_request_settings
    except AttributeError:
        advisor_settings = None
    if not advisor_settings:
        advisor_settings = initialize_advisor_request_settings_for_project(
            project, kwargs.get('user_from'))

    for team in project.teams.all():
        create_team_group(project, team)


def post_advisor_request_save(sender, instance, created, *args, **kwargs):
    project = instance.project
    for team in project.teams.all():
        try:
            opportunity_group = team.opportunity_group
        except AttributeError:
            continue
        OpportunityGroupUpdateTask().s(
            settings_id=instance.id,
            group_uuid=opportunity_group.group_uuid.__str__()).apply_async()


def new_team_handler(sender, instance, created, *args, **kwargs):
    project = instance.project
    try:
        advisor_settings = project.advisor_request_settings
    except AttributeError:
        advisor_settings = None
    if not advisor_settings:
        return
    if created and not project.is_draft:
        OpportunityGroupCreateTask().s(
            team_id=instance.id,
            user_id=project.created_by.id).apply_async()


def delete_team_handler(sender, instance, *args, **kwargs):
    try:
        opportunity_group = instance.opportunity_group
    except AttributeError:
        opportunity_group = None
    if not opportunity_group:
        return
    OpportunityGroupDeleteTask().s(
        group_uuid=opportunity_group.group_uuid.__str__()).apply_async()
