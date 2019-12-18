from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.conf import settings

from permissions.shortcuts import has_project_perms
from exo_role.models import ExORole

from ..signals_define import signal_team_coach_updated


class TeamMemberMixin:
    member_permission = settings.PROJECT_PERMS_CRUD_TEAM

    def check_member_perms(self, user_from):
        if not has_project_perms(
            self.project,
            self.member_permission,
            user_from,
        ):
            raise ValidationError('No permissions to edit team')

    def add_member(self, user_from, email, name):
        self.check_member_perms(user_from)

        new_member = self.project.add_user_project_member(
            user_from=user_from,
            email=email,
            name=name,
        )
        try:
            self.team_members.add(new_member)
        except IntegrityError:
            pass

        exo_role = ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)
        self.project.users_roles.get_or_create_user(
            user_from=user_from,
            user=new_member,
            project=self.project,
            exo_role=exo_role)

        return new_member

    def get_member(self, email):
        try:
            return self.team_members.get(email=email)
        except get_user_model().DoesNotExist:
            return None

    def remove_member(self, user_from, user):
        self.check_member_perms(user_from)
        self.team_members.remove(user)

    def update_members(self, user_from, members):
        self.check_member_perms(user_from)
        previous_emails = set(self.team_members.all().values_list(
            'email',
            flat=True,
        ))
        new_emails = []
        for new_member in members:
            new_emails.append(new_member.get('email'))
            member = self.get_member(email=new_member.get('email'))
            if not member:
                name = new_member.get('short_name')
                if not name:
                    name = new_member.get('name')
                self.add_member(
                    user_from=user_from,
                    email=new_member.get('email'),
                    name=name,
                )

        for old_email in previous_emails - set(new_emails):
            member = self.get_member(email=old_email)
            self.remove_member(user_from, member)


class TeamCoachMixin:

    def check_coach_project_role(self, consultant):
        active_coaches = self.project.consultants_roles.get_team_manager_consultants(
            self.project,
        ).consultants()

        if consultant not in active_coaches:
            raise ValidationError('User is not available to be a Coach for this team')

    def update_coach(self, user_from, coach):
        self.check_member_perms(user_from)
        self.check_coach_project_role(coach)

        if coach != self.coach:
            old_coach = self.coach
            self.coach = coach
            self.save(update_fields=['coach'])

            signal_team_coach_updated.send(
                sender=self,
                team=self,
                new_coach=self.coach,
                old_coach=old_coach,
            )
