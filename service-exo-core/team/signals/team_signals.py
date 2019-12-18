from invitation.models import Invitation

from ..conf import settings
from ..signals_define import signal_team_coach_updated


def _delete_all_team_coach_perms(team, coach):

    if coach:
        # TODO take care about the invitation for this user

        if not team.team_members.filter(pk=coach.user.pk).exists():
            team.remove_permission(
                settings.TEAM_PERMS_FULL_VIEW_TEAM,
                coach.user,
            )
        team.remove_permission(
            settings.TEAM_PERMS_COACH_TEAM,
            coach.user,
        )


def signal_update_team_coach(
        sender, team, new_coach, old_coach,
        *args, **kwargs):
    """
        Team Coach has changed, so we need to update permissions for
        each one
    """
    if old_coach:
        _delete_all_team_coach_perms(team, old_coach)

    # Add new permissions
    team.add_permission(
        settings.TEAM_PERMS_FULL_VIEW_TEAM,
        new_coach.user,
    )
    team.add_permission(
        settings.TEAM_PERMS_COACH_TEAM,
        new_coach.user,
    )

    Invitation.objects.create_team_invitation(
        from_user=team.created_by,
        to_user=team.coach.user,
        related_object=team,
        autosend=team.project.autosend(consultant=True),
        status=settings.INVITATION_STATUS_CH_ACTIVE
        if team.project.autoactive else settings.INVITATION_STATUS_CH_PENDING,
    )


def signal_create_team(sender, instance, created, *args, **kwargs):

    if created:
        signal_team_coach_updated.send(
            sender=sender,
            team=instance,
            new_coach=instance.coach,
            old_coach=None,
        )


def signal_delete_team(sender, instance, *args, **kwargs):
    # Task permission for the Team

    _delete_all_team_coach_perms(instance, instance.coach)

    for member in instance.team_members.all():
        other_team = sender.objects.filter(
            project=instance.project,
            team_members=member,
        )
        if not other_team:
            instance.project.remove_permission(
                settings.PROJECT_PERMS_VIEW_PROJECT,
                member,
            )


def signal_pre_delete_team(sender, instance, *args, **kwargs):
    # Task permission for the Team
    for member in instance.team_members.all():
        other_team = sender.objects.filter(
            project=instance.project,
            team_members=member,
        ).exclude(pk=instance.pk)
        if not other_team:
            instance.project.remove_permission(
                settings.PROJECT_PERMS_VIEW_PROJECT,
                member,
            )
