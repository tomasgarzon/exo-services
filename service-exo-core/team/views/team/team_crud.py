from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.shortcuts import Http404
from django.urls import reverse_lazy

from project.views.mixin import ProjectPermissionMixin
from utils.mixins import DeleteMessageMixin

from ...models import Team
from ...conf import settings
from ...forms.team import (
    TeamForm,
    TeamSprintAutomatedForm,
    TeamGenericProjectForm,
)


class TeamCUMixin(ProjectPermissionMixin):
    model = Team
    project_permission_required = settings.PROJECT_PERMS_CRUD_TEAM
    template_name = 'team/team_form.html'
    form_class = {
        settings.PROJECT_CH_TYPE_SPRINT_AUTOMATED: TeamSprintAutomatedForm,
        settings.PROJECT_CH_TYPE_GENERIC_PROJECT: TeamGenericProjectForm,
    }

    def get_form_class(self):
        return self.form_class.get(
            self.get_project().type_project_lower, TeamForm)

    def get_form_kwargs(self, *args, **kwargs):
        project = self.get_project()
        response = super().get_form_kwargs(*args, **kwargs)
        response['project'] = project
        return response

    def post(self, request, *args, **kwargs):
        raise Http404


class TeamCreateView(TeamCUMixin, CreateView):
    pass


class TeamEditView(TeamCUMixin, UpdateView):
    pass


class TeamDetailView(ProjectPermissionMixin, DetailView):
    model = Team
    template_name = 'team/team_detail.html'


class TeamDeleteView(
        DeleteMessageMixin,
        ProjectPermissionMixin,
        DeleteView):

    model = Team
    project_permission_required = settings.PROJECT_PERMS_CRUD_TEAM
    template_name = 'team/team_confirm_delete.html'
    delete_message = '%(name)s was removed successfully'

    def get_delete_message(self):
        return self.delete_message % {'name': self.get_object().name}

    def get_success_url(self):
        project = self.get_project()
        return reverse_lazy(
            'project:team:list',
            kwargs={'project_id': project.pk},
        )
