from django.views.generic import RedirectView
from django.urls import reverse_lazy
from django.contrib import messages

from project.views.mixin import ProjectPermissionMixin

from ..models import Validation


class RunValidationView(
        ProjectPermissionMixin,
        RedirectView
):

    def get_redirect_url(self, project_id):
        return reverse_lazy('project:project:validations:list', args=[project_id])

    def get(self, request, project_id):
        project = self.get_project()
        ValidatorClass = project.real_type.validator_class()
        validator = ValidatorClass(project)
        validator.validate()
        has_errors_pending = Validation.objects.filter_by_project(
            project,
        ).filter_by_validation_type_error().filter_by_status_pending().exists()
        if has_errors_pending:
            messages.error(request, 'This project has some errors')
        else:
            has_warning_pending = Validation.objects.filter_by_project(
                project,
            ).filter_by_validation_type_warning().filter_by_status_pending().exists()
            if has_warning_pending:
                messages.warning(
                    request, "This project doesn't have errors, but it has some warnings",
                )
            else:
                messages.success(request, 'The project is ready for lunch')
        return super().get(request, project_id)
