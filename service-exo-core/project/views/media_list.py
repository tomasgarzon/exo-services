import logging

from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.urls import reverse
from django.shortcuts import redirect

from .mixin import ProjectPermissionMixin
from ..conf import settings
from ..forms import ProjectTypeForm

logger = logging.getLogger('library')


class MediaLibraryProjectResourcesView(
        ProjectPermissionMixin,
        ListView):
    http_method_names = ['get']
    template_name = 'project/media/media_project_list.html'
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGER
    paginate_by = 10000

    def get_queryset(self):
        project = self.get_project()
        page = self.request.GET.get('page', 1)
        response = project.get_resources_from_media_library(
            user_from=self.request.user,
            page=page,
            page_size=self.paginate_by,
            uuid=project.uuid)

        return [] if not response or not response.ok else response.json().get('results')


class MediaLibraryAddResourcesView(
        ProjectPermissionMixin,
        ListView):
    http_method_names = ['get', 'post']
    template_name = 'project/media/media_list.html'
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGER
    paginate_by = 10000

    def get_queryset(self):
        project = self.get_project()
        page = self.request.GET.get('page', 1)
        response = project.get_resources_from_media_library(
            user_from=self.request.user,
            page=page,
            page_size=self.paginate_by)

        return [] if not response or not response.ok else response.json().get('results')

    def post(self, request, **kwargs):
        resources_selected = request.POST.getlist('resources')
        project = self.get_project()
        for resource_pk in resources_selected:
            project.add_resource_to_project(
                resource_pk=resource_pk,
                user_from=request.user)

        messages.success(request, 'Media added')

        return redirect(reverse('project:project:media', kwargs={'project_id': project.id}))


class MediaLibraryProjectResourceDeleteView(ProjectPermissionMixin, TemplateView):
    http_method_names = ['get', 'post']
    template_name = 'project/media/media_delete.html'
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGER

    def get_success_url(self):
        return reverse('project:project:media', kwargs={'project_id': self.project.id})

    def post(self, request, **kwargs):
        project = self.get_project()
        resource_pk_from_library = kwargs.get('resource_pk')
        project.remove_resource_to_project(
            resource_pk=resource_pk_from_library,
            user_from=self.request.user)

        messages.success(request, 'Media deleted')

        return redirect(self.get_success_url())


class MediaLibraryProjectPopulateView(ProjectPermissionMixin, FormView):
    http_method_names = ['get', 'post']
    template_name = 'project/media/media_populate.html'
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGER
    form_class = ProjectTypeForm

    def get_success_url(self):
        return reverse('project:project:media', kwargs={'project_id': self.project.id})

    def post(self, request, **kwargs):
        project = self.get_project()
        _type = request.POST.get('_type')

        project.assign_resources_from_media_library(request.user, _type)

        messages.success(request, 'Media populated')

        return redirect(self.get_success_url())
