import logging

from django.conf import settings

from utils.remote_user import create_remote_user, check_if_exists_email
from utils.users import merge_users
from team.models import UserTeamRole
from utils.mails.handlers import mail_handler

from ...signals_define import project_post_launch
from ..user_project_role import UserProjectRole
from ...mails import MemberLaunch


logger = logging.getLogger('service')


class ProjectExecutionMixin:

    def set_start(self, user):
        self.set_status(user, settings.PROJECT_CH_STATUS_STARTED)

    def set_finish(self, user):
        self.set_status(user, settings.PROJECT_CH_STATUS_FINISH)

    def sync_launch(self, user):
        self._active_roles(user)
        self.set_status(user, settings.PROJECT_CH_STATUS_WAITING)

    def launch(self, user, message=None, start_date=None):
        users_created = self._create_participants(user)
        try:
            self._send_members_email(user, users_created, message)
        except Exception:
            logger.error('Error sending emails for launching project {}'.format(self.name))
        project_post_launch.send(
            sender=self.__class__,
            project=self,
            user_from=user)

    def _send_members_email(self, user_from, users_created=[], message=None):
        if settings.POPULATOR_MODE and not settings.TEST_MODE:
            return
        for user in self.members:
            user_data = MemberLaunch(self, user).get_data()
            if message is not None:
                user_data['message'] = message
            if user in users_created:
                user_data['password'] = self.settings.launch['default_password']
            email_name = settings.PROJECT_EMAIL_MEMBER_LAUNCH
            mail_handler.send_mail(
                template=email_name,
                recipients=[user_data.pop('email')],
                **user_data)

    def _active_roles(self, user_from):
        for user_role in UserProjectRole.objects.filter(project_role__project=self):
            user_role.activate(user_from)
        for user_role in UserTeamRole.objects.filter(team__project=self):
            user_role.activate(user_from)

    def _create_participants(self, user_from):
        users_created = []
        participants_project_role = UserProjectRole.objects.filter_by_project(
            self).filter_by_role(settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)
        for user_project_role in participants_project_role:
            user = user_project_role.user
            if hasattr(user, 'participant'):
                user_data, exists = self.check_remote_user(user.participant.email)
                if exists:
                    merge_users(user, user_data.get('uuid'))
                else:
                    created = self.create_remote_user(user_from, user, user.participant)
                    if created:
                        users_created.append(user)
        return users_created

    def create_remote_user(self, user_from, user, participant):
        user_data = create_remote_user(user_from, self, participant)
        if user_data is None:
            return
        user.uuid = user_data['uuid']
        user.save()
        participant.delete()
        return user_data['created']

    def check_remote_user(self, email):
        return check_if_exists_email(email)
