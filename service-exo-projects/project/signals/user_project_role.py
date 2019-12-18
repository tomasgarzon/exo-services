def post_save_user_project_role(sender, instance, created, *args, **kwargs):
    instance.project_role.project.refresh_permissions_for_user(instance.user)


def post_delete_user_project_role(sender, instance, *args, **kwargs):
    instance.project_role.project.refresh_permissions_for_user(instance.user)
    project_role = instance.project_role
    user = instance.user
    team_roles = user.user_team_roles.filter(
        team_role__code=project_role.code,
        team__project=project_role.project)

    for user_team_role in team_roles:
        user_team_role.delete()
