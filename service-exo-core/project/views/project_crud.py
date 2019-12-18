import csv

from django.conf import settings
from django.views.generic.edit import DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.utils import timezone

from guardian.mixins import PermissionRequiredMixin as \
    GuardianPermissionRequiredMixin

from utils.mixins import DeleteMessageMixin

from ..models import Project
from .mixin_public_object_names import PublicObjectNamesMixin


class ProjectDetailView(
    GuardianPermissionRequiredMixin,
    PublicObjectNamesMixin,
    DetailView
):

    model = Project
    template_name = 'project/project_detail.html'
    permission_required = settings.PROJECT_PERMS_VIEW_PROJECT
    return_404 = True


class ProjectDeleteView(
        DeleteMessageMixin,
        PermissionRequiredMixin,
        PublicObjectNamesMixin,
        DeleteView
):

    model = Project
    permission_required = settings.PROJECT_PERMS_DELETE_PROJECT
    delete_message = '%(name)s was removed successfully'
    success_url = reverse_lazy('project:service-list')
    _suffix_list = 'list'
    raise_exception = True

    def get_delete_message(self):
        return self.delete_message % {
            'name': self.get_public_object_name(),
        }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['url_cancel'] = self.get_success_url()
        return context


class ProjectExportAsCSVView(ProjectDetailView):

    def get(self, request, *args, **kwargs):
        header = [
            'Name', 'email', 'Joined',
        ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="project_{}_{}.csv"'.format(
            kwargs['pk'], timezone.now().strftime('%Y_%m_%d'))
        writer = csv.writer(response)
        writer.writerow(header)
        CODE = settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT

        for item in self.get_object().users_roles.filter_by_exo_role_code(CODE):
            row = [
                item.user.get_full_name(),
                item.user.email,
                item.created.strftime('%Y-%m-%d'),
            ]

            writer.writerow(row)

        return response
