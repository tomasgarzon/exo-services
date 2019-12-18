from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin

from permissions.helpers import (
    get_project_403_or_None, get_team_403_or_None
)
from team.models import Team

from ..models import Project
from ..conf import settings


class ProjectPermissionMixin(GuardianPermissionRequiredMixin):
    """
        project_id required in kwargs (url)
    """
    permission_required = settings.PROJECT_PERMS_VIEW_PROJECT
    return_404 = True

    def get_project(self):
        if not self.kwargs.get('project_id'):
            raise Http404
        self.project = Project.objects.get(id=self.kwargs.get('project_id'))
        return self.project

    def get_team(self):
        raise Http404

    def get_permission_object(self):
        return self.get_project()

    def get_context_data(self, *args, **kwargs):
        self.get_project()
        context = super().get_context_data(*args, **kwargs)
        context['project'] = self.project
        return context

    def check_permissions(self, request):
        forbidden = super().check_permissions(request)
        if forbidden:
            return forbidden
        project_permission_required = getattr(self, 'project_permission_required', None)
        if project_permission_required:
            related_key = getattr(self, 'related_permission_object', None)
            if related_key:
                related_object = getattr(self, related_key, None)
            else:
                related_object = None
            forbidden = get_project_403_or_None(
                request,
                project_permission_required,
                self.get_project(),
                obj=related_object,
                return_403=True)
        if forbidden:
            self.on_permission_check_fail(request, forbidden, obj=self.project)

        team_permission_required = getattr(self, 'team_permission_required', None)
        if team_permission_required:
            related_key = getattr(self, 'related_permission_object', None)
            if related_key:
                related_object = getattr(self, related_key, None)
            else:
                related_object = None
            forbidden = get_team_403_or_None(
                request,
                team_permission_required,
                self.get_team(),
                obj=related_object,
                return_403=True)
        if forbidden:
            self.on_permission_check_fail(request, forbidden, obj=self.project)
        return forbidden


class SprintAutomatedProjectTeamPermission(ProjectPermissionMixin):
    team_permission_required = settings.TEAM_PERMS_FULL_VIEW_TEAM

    def get_project(self):
        super().get_project()
        if not self.project.is_version_2:
            raise Http404

        return self.project

    def get_team(self):
        team_id = self.kwargs.get('team_id')
        if not team_id:
            raise Http404
        try:
            self.team = Team.objects.get(id=team_id)
        except ObjectDoesNotExist:
            raise Http404
        return self.team


class ProjectQuerySetListView(object):
    def get_queryset(self, queryset=None):
        if queryset is None:
            queryset = self.model.objects.filter_by_project(self.get_project())
        self.form_filter.is_valid()
        data = self.form_filter.cleaned_data
        queryset = queryset.filter_complex(*data, **data)
        return queryset.distinct()
