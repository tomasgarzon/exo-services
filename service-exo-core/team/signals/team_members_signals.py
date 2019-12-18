from invitation.models import Invitation

from ..conf import settings


def signal_new_member_added(sender, **kwargs):
    """
        New User is added as TeamMember
    """
    action = kwargs.get('action')
    # The new member is already added
    if action == 'post_add':
        team = kwargs.get('instance')
        member_class = kwargs.get('model')
        member_set = kwargs.get('pk_set')

        if not member_set:
            return

        member_id = list(member_set)[0]
        member = member_class.objects.get(id=member_id)

        Invitation.objects.create_team_invitation(
            from_user=team.coach.user,
            to_user=member,
            related_object=team,
            autosend=team.project.autosend(),
            status=settings.INVITATION_STATUS_CH_ACTIVE
            if team.project.autoactive else settings.INVITATION_STATUS_CH_PENDING,
        )

    if action == 'post_remove':
        team = kwargs.get('instance')
        member_class = kwargs.get('model')
        member_set = kwargs.get('pk_set')

        if not member_set:
            return

        member_id = list(member_set)[0]
        member = member_class.objects.get(id=member_id)

        team.remove_permission(settings.TEAM_PERMS_FULL_VIEW_TEAM, member)

        other_team = team.project.teams.filter(team_members=member).exclude(pk=team.pk)

        if not other_team:
            team.project.users_roles.filter_by_user(member).filter_by_exo_role_code(
                settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT).delete()

        Invitation.objects.filter_by_object(team).filter(user=member).delete()
