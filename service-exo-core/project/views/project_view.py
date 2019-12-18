from django.views.generic.edit import UpdateView
from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse

from project.views.mixin import ProjectPermissionMixin
from generic_project.forms import GenericProjectForm
from sprint.forms.sprint import SprintSimpleForm
from sprint_automated.forms.sprint_automated import SprintAutomatedSimpleForm
from fastrack.forms import FastrackSprintForm
from utils.dates import localize_date
from opportunities.helper import initialize_advisor_request_settings_for_project

from ..forms import ProjectSettingsForm
from ..models import Project


class ProjectGeneralView(ProjectPermissionMixin, SuccessMessageMixin, UpdateView):

    template_name = 'project/project_form.html'
    model = Project
    project_permission_required = settings.PROJECT_PERMS_EDIT_PROJECT
    pk_url_kwarg = 'project_id'
    success_message = 'Project saved successfully'
    form_class = {
        settings.PROJECT_CH_TYPE_SPRINT: SprintSimpleForm,
        settings.PROJECT_CH_TYPE_SPRINT_AUTOMATED: SprintAutomatedSimpleForm,
        settings.PROJECT_CH_TYPE_GENERIC_PROJECT: GenericProjectForm,
        settings.PROJECT_CH_TYPE_FASTRACKSPRINT: FastrackSprintForm,
    }
    return_404 = None

    def get_initial(self, *args, **kwargs):
        settings = self.get_project().settings
        initial = {
            'send_welcome_consultant': settings.launch['send_welcome_consultant'],
            'send_welcome_participant': settings.launch['send_welcome_participant'],
            'fix_password': settings.launch['fix_password'],
        }
        if self.get_project().start:
            project = self.get_project()
            initial['start'] = localize_date(project.start, time_zone=project.timezone).strftime('%Y-%m-%d %H:%M:%S')
        return initial

    def get_object(self):
        project = super().get_object()
        return project.real_type

    def get_form_class(self):
        return self.form_class.get(self.get_object().type_project_lower)

    def get_success_message(self, data):
        return '{} saved successfully'.format(self.get_object().type_project)


class ProjectSettingsView(ProjectPermissionMixin, SuccessMessageMixin, UpdateView):

    template_name = 'project/settings/form.html'
    form_class = ProjectSettingsForm
    model = Project
    project_permission_required = settings.PROJECT_PERMS_EDIT_PROJECT
    pk_url_kwarg = 'project_id'
    success_message = 'Project saved successfully'

    def get_initial(self, *args, **kwargs):
        project = self.get_project()
        settings = project.settings
        initial = {
            'send_welcome_consultant': settings.launch['send_welcome_consultant'],
            'send_welcome_participant': settings.launch['send_welcome_participant'],
            'fix_password': settings.launch['fix_password'],
            'participant_step_feedback_enabled': settings.participant_step_feedback_enabled,
            'participant_step_microlearning_enabled': settings.participant_step_microlearning_enabled,
            'hide_from_my_jobs': settings.hide_from_my_jobs,
            'version': settings.version,
            'template_assignments': settings.template_assignments,
            'team_communication_enabled': settings.team_communication,
            'ask_to_ecosystem_enabled': settings.ask_to_ecosystem,
            'directory_enabled': settings.directory,
            'advisor_request_enabled': settings.advisor_request,
        }
        try:
            advisor_request_settings = project.advisor_request_settings
        except Exception:
            advisor_request_settings = initialize_advisor_request_settings_for_project(project, project.created_by)
        initial['num_tickets_per_team'] = advisor_request_settings.total
        try:
            initial['tickets_price'] = advisor_request_settings.budgets[0]['budget']
        except IndexError:
            initial['tickets_price'] = 0
        try:
            initial['tickets_currency'] = advisor_request_settings.budgets[0]['currency']
        except IndexError:
            initial['tickets_currency'] = 0
        return initial

    def get_success_message(self, data):
        return '{} saved successfully'.format(self.get_object().type_project)

    def get_success_url(self):
        return reverse('project:project:settings', args=[self.get_project().pk])
