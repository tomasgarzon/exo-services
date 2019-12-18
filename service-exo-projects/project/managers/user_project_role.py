import uuid

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.db import transaction

from utils.remote_user import check_if_exists_email

from ..models import Participant
from ..queryset.user_project_role import UserProjectRoleQuerySet


class UserProjectRoleManager(models.Manager):
    use_for_related_fields = True
    queryset_class = UserProjectRoleQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

    def filter_by_role(self, role):
        return self.get_queryset().filter_by_role(role)

    def filter_by_level(self, level):
        return self.get_queryset().filter_by_level(level)

    def filter_by_manager(self):
        return self.get_queryset().filter_by_manager()

    def create(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        teams = kwargs.pop('teams', None)
        if team:
            teams = [team]
        try:
            with transaction.atomic():
                user_project_role = super().create(*args, **kwargs)
        except IntegrityError:
            user_project_role = self.get(
                user=kwargs.get('user'),
                project_role=kwargs.get('project_role'))
        project = user_project_role.project
        if not project.is_draft:
            user_project_role.activate(user_project_role.created_by)
        if teams:
            role = project.team_roles.filter(code=user_project_role.project_role.code).first()
            if role:
                for team in teams:
                    team.user_team_roles.create(
                        created_by=user_project_role.created_by,
                        user=user_project_role.user,
                        team_role=role)
        return user_project_role

    def create_participant(self, **validated_data):
        name = validated_data.pop('name')
        email = validated_data.pop('email')
        project = validated_data.pop('project')
        participant = Participant.objects.filter(email=email)
        if participant.exists():
            participant = participant.first()
            user = participant.user
        else:
            remote_user, exists = check_if_exists_email(email)
            if exists:
                user, created = get_user_model().objects.get_or_create(
                    uuid=remote_user.get('uuid'),
                    defaults={
                        'is_active': True,
                    }
                )
            else:
                user, created = get_user_model().objects.get_or_create(
                    uuid=uuid.uuid4(),
                    defaults={
                        'is_active': True,
                    }
                )
                if created:
                    participant = Participant.objects.create(
                        user=user,
                        name=name,
                        email=email)
        if not project.is_draft and participant:
            project.create_remote_user(
                validated_data.get('created_by'),
                user, participant)
        validated_data['user'] = user
        validated_data['project_role'] = project.project_roles.get(
            code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)
        return self.create(**validated_data)

    def update_teams_in_project(self, user_from, project, user, code, teams):
        current_teams = user.user_team_roles.filter(team__project=project).teams()
        teams_deleted = set(current_teams) - set(teams)
        user.user_team_roles.filter(team__in=teams_deleted).delete()

        new_teams = set(teams) - set(current_teams)
        role = project.team_roles.filter(code=code).first()
        for team in new_teams:
            team.user_team_roles.create(
                created_by=user_from,
                user=user,
                team_role=role)

    def update_user_in_project(self, user_from, project, user, project_roles, teams):
        self.update_teams_in_project(
            user_from=user_from,
            project=project,
            user=user,
            code=settings.EXO_ROLE_CODE_SPRINT_COACH,
            teams=teams)

        current_roles = user.user_project_roles.filter(project_role__project=project).roles()
        roles_deleted = set(current_roles) - set(project_roles)
        user.user_project_roles.filter(project_role__in=roles_deleted).delete()

        new_roles = set(project_roles) - set(current_roles)
        for role in new_roles:
            self.create(
                user=user,
                created_by=user_from,
                project_role=role,
                teams=[])

    def update_participant_in_project(self, user_from, project, user, name, email, teams):
        participant = user.participant
        participant.name = name
        participant.email = email
        participant.save()

        self.update_teams_in_project(
            user_from=user_from,
            project=project,
            user=user,
            code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
            teams=teams)
