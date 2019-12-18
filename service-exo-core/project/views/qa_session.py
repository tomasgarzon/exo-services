from django.conf import settings
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

from project.views.mixin import ProjectPermissionMixin
from utils.mixins import DeleteMessageMixin
from qa_session.models import QASession
from qa_session.forms import QASessionForm
from utils.dates import localize_date


class QASessionListView(
        ProjectPermissionMixin,
        ListView
):
    template_name = 'project/qa_sessions/list.html'
    model = QASession
    paginate_by = 30
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGER

    def get_queryset(self):
        return self.model.objects.filter(project=self.get_project())


class QASessionCUMixin(ProjectPermissionMixin, SuccessMessageMixin):
    model = QASession
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGER
    template_name = 'project/qa_sessions/form.html'
    form_class = QASessionForm

    def get_success_url(self):
        project = self.get_project()
        return reverse_lazy(
            'project:project:swarm-session',
            kwargs={'project_id': project.pk},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'project': self.get_project(),
        })
        return kwargs


class QASessionEditView(QASessionCUMixin, UpdateView):

    def get_initial(self, *args, **kwargs):
        data = super().get_initial(*args, **kwargs)
        consultants = self.get_object().members.consultants()
        data['consultants'] = consultants
        data['start_at'] = localize_date(
            self.get_object().start_at,
            time_zone=self.get_project().timezone).strftime('%Y-%m-%d %H:%M:%S')
        data['end_at'] = localize_date(
            self.get_object().end_at,
            time_zone=self.get_project().timezone).strftime('%Y-%m-%d %H:%M:%S')
        return data


class QASessionAddView(QASessionCUMixin, CreateView):

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.created_by = self.request.user
        self.object.save()
        return response


class QASessionDetailView(ProjectPermissionMixin, DetailView):
    model = QASession
    template_name = 'project/qa_sessions/detail.html'


class QASessionDeleteView(
        DeleteMessageMixin,
        ProjectPermissionMixin,
        DeleteView):

    model = QASession
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGER
    template_name = 'project/qa_sessions/qa_session_confirm_delete.html'
    delete_message = '%(name)s was removed successfully'

    def get_delete_message(self):
        return self.delete_message % {'name': self.get_object().name}

    def get_success_url(self):
        project = self.get_project()
        return reverse_lazy(
            'project:project:swarm-session',
            kwargs={'project_id': project.pk},
        )
