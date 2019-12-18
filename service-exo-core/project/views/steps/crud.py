from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

from project.views.mixin import ProjectPermissionMixin

from ...models import Step
from ...conf import settings


class StepCUMixin(ProjectPermissionMixin, SuccessMessageMixin):
    model = Step
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGER
    template_name = 'project/steps/form.html'

    def get_success_url(self):
        project = self.get_project()
        return reverse_lazy('project:project:steps', kwargs={'project_id': project.pk})

    def get_form(self, form_class=None):
        return self.form_class(**self.get_form_kwargs())

    def get_success_message(self, validated_data):
        step = self.get_object()
        return '{} was modified successfully'.format(step)
