from django.db import models
from django.conf import settings

from exo_role.models import ExORole
from relation.models import ConsultantProjectRole
from permissions.shortcuts import has_project_perms

from ..querysets.team import TeamQuerySet


class TeamManager(models.Manager):
    use_for_related_fields = True
    queryset_class = TeamQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

    def filter_by_stream(self, stream):
        return self.get_queryset().filter_by_stream(stream)

    def filter_by_stream_edge(self):
        return self.get_queryset().filter_by_stream_edge()

    def filter_by_stream_core(self):
        return self.get_queryset().filter_by_stream_core()

    def create(self, user_from, project, name, coach, *args, **kwargs):
        """
        User: the user that creates the object
        Members must be a dict {'name': '', 'email': ''}
        """
        # Create the ConsultantProjectRole for this consultant
        #  with a Coach role if don't exist
        # Check for permissions for the user
        has_project_perms(
            project,
            settings.PROJECT_PERMS_CRUD_TEAM,
            user_from,
        )

        role_code = project.customize.get('roles').get('team_manager')[0]

        exo_role = ExORole.objects.get(code=role_code)
        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=user_from, consultant=coach, project=project, exo_role=exo_role)

        stream = kwargs.get('stream')
        team = self.model(
            created_by=kwargs.get('created_by'),
            project=project,
            name=name,
            coach=coach,
            stream=stream,
        )

        team.save()
        team.zoom_id = kwargs.get('zoom_id', None)

        for member in kwargs.get('team_members', []):
            team.add_member(
                user_from=user_from,
                email=member.get('email'),
                name=member.get('short_name'),
            )
        return team

    def update(self, instance, user_from, name, coach, *args, **kwargs):
        has_project_perms(instance.project, settings.PROJECT_PERMS_CRUD_TEAM, user_from)
        instance.name = name
        instance.stream = kwargs.get('stream')
        instance.zoom_id = kwargs.get('zoom_id', None)
        instance.save(update_fields=['name', 'stream', 'slug'])

        role_code = instance.project.customize.get('roles').get('team_manager')[0]

        exo_role = ExORole.objects.get(code=role_code)
        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=user_from, consultant=coach, project=instance.project, exo_role=exo_role)

        instance.update_coach(user_from, coach)
        instance.update_members(user_from, kwargs.get('team_members', []))
        instance.refresh_from_db()
        return instance
