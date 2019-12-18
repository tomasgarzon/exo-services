from project.tasks import MemberAddedTeamTask


def post_save_user_team_role(sender, instance, created, *args, **kwargs):
    instance.team.refresh_permissions_for_user(instance.user)
    team = instance.team
    first_role_in_team = not instance.user.user_team_roles.filter(
        team=team).exclude(pk=instance.pk).exists()
    if first_role_in_team and not team.project.is_draft:
        MemberAddedTeamTask().s(
            team_id=team.pk,
            user_id=instance.user.id).apply_async()


def post_delete_user_team_role(sender, instance, *args, **kwargs):
    instance.team.refresh_permissions_for_user(instance.user)
