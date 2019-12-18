from django.conf import settings

from utils.generic.list import ListFilterView
from project.views.mixin import ProjectPermissionMixin, ProjectQuerySetListView

from ...forms import StepSearchListForm
from ...models import Step


class StepListView(
        ProjectPermissionMixin,
        ProjectQuerySetListView,
        ListFilterView):
    template_name = 'project/steps/list.html'
    model = Step
    paginate_by = 30
    filter_form_class = StepSearchListForm
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGER
