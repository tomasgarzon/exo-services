from django.views.generic.base import TemplateView

from braces import views

from project.models import Project
from custom_auth.models import InternalOrganization


class AdminDashboardView(
    views.LoginRequiredMixin,
    views.StaffuserRequiredMixin,
    TemplateView
):

    template_name = 'dashboard/home.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['projects'] = Project.objects.filter_by_user_or_organization(
            self.request.user).actives()

        finished_projects = Project.objects.filter_by_user_or_organization(
            self.request.user).finished()
        context['finished_projects'] = sorted(
            finished_projects,
            key=lambda prj: prj.type_project,
        )

        context['internal_organizations'] = InternalOrganization.objects.filter(
            users_roles__user=self.request.user)
        return context
