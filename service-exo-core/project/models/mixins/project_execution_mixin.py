from django.conf import settings

from invitation.models import Invitation

from ...signals_define import project_post_launch


class ProjectExecutionMixin:

    def set_started(self, user, start_date):
        if self.is_draft:
            self.launch(user, start_date)
        self.start = start_date
        self.status = settings.PROJECT_CH_PROJECT_STATUS_STARTED
        self.save(update_fields=['start', 'status'])

    def set_finished(self, user, end_date):
        self.end = end_date
        self.status = settings.PROJECT_CH_PROJECT_STATUS_FINISHED
        self.save(update_fields=['end', 'status'])

    def launch(self, user, start_date=None):
        if start_date:
            self.start = start_date
        self.status = settings.PROJECT_CH_PROJECT_STATUS_WAITING
        self.save(update_fields=['start', 'status', 'modified'])
        self._send_consultants_invitation(user)
        self._send_users_invitation(user)
        self._send_team_invitations(user)

        project_post_launch.send(sender=self.__class__, project=self, user=user)

    def _send_consultants_invitation(self, user, autoaccept=True):
        for role in self.consultants_roles.all():
            invitation = Invitation.objects.filter_by_object(role)
            if not invitation:
                continue
            invitation = invitation.get()
            if self.settings.launch['send_welcome_consultant']:
                invitation.invitation_related.send_notification(user)
            if invitation.is_pending and autoaccept:
                invitation.accept(user)

    def _send_users_invitation(self, user, autoaccept=True):
        for role in self.users_roles.all():
            user_invitation = Invitation.objects.filter_by_object(role)
            if user_invitation:
                invitation = user_invitation[0]
                if self.settings.launch['send_welcome_participant']:
                    invitation.invitation_related.send_notification(user)
                if invitation.is_pending and autoaccept:
                    invitation.accept(user)
            user_role = role.user
            if self.settings.launch['fix_password'] and not user_role.password_updated:
                user_role.set_password(self.settings.launch['fix_password'])
                user_role.save()

    def _send_team_invitations(self, user, autoaccept=True):
        for team in self.teams.all():
            invitations = Invitation.objects.filter_by_object(team)
            for inv in invitations:
                if inv.is_pending and autoaccept:
                    inv.accept(inv.user)
