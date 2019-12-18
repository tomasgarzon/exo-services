from django.views.generic.detail import DetailView
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from project.views.mixin import ProjectPermissionMixin
from project.models import Step

from ..models import MicroLearning
from ..forms.microlearning_step import MicroLearningFactory


class EditMicrolearningStepView(ProjectPermissionMixin, DetailView):
    model = Step
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGER
    form_class = MicroLearningFactory
    template_name = 'learning/steps/microlearning_form.html'

    def get_success_url(self):
        project = self.get_project()
        return reverse_lazy(
            'project:steps',
            kwargs={'project_id': project.pk},
        )

    def get_form_kwargs(self):
        for stream in self.get_object().streams.all():
            MicroLearning.objects.get_or_create(
                step_stream=stream,
            )
        kwargs = {
            'queryset': MicroLearning.objects.filter(step_stream__step=self.get_object()),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_form(self, form_class=None):
        return self.form_class(**self.get_form_kwargs())

    def get(self, request, project_id, pk):
        self.form = self.get_form()
        return super().get(request, project_id, pk)

    def get_success_message(self):
        step = self.get_object()
        return 'Microlearning for {} were modified successfully'.format(step)

    def post(self, request, project_id, pk):
        self.form = self.get_form()
        if self.form.is_valid():
            self.form.save()
            messages.success(request, self.get_success_message())
            return redirect(self.get_success_url())
        else:
            return super().get(request, project_id, pk)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form'] = self.form
        return context
