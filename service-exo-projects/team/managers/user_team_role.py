from django.db import models
from django.db.utils import IntegrityError
from django.db import transaction

from ..queryset.user_team_role import UserTeamRoleQuerySet


class UserTeamRoleManager(models.Manager):
    use_for_related_fields = True
    queryset_class = UserTeamRoleQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

    def filter_by_role(self, role):
        return self.get_queryset().filter_by_role(role)

    def filter_by_team(self, team):
        return self.get_queryset().filter_by_team(team)

    def filter_by_level(self, level):
        return self.get_queryset().filter_by_level(level)

    def filter_by_manager(self):
        return self.get_queryset().filter_by_manager()

    def create(self, *args, **kwargs):
        try:
            with transaction.atomic():
                new_role = super().create(*args, **kwargs)
        except IntegrityError:
            new_role = self.get(
                user=kwargs.get('user'),
                team=kwargs.get('team'),
                team_role=kwargs.get('team_role'))
        if not new_role.team.project.is_draft:
            new_role.activate(new_role.created_by)
        return new_role
