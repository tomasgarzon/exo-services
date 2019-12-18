from django.views.generic.list import ListView

from project.views.mixin import ProjectPermissionMixin

from ..models import AssignmentStep
from ..forms.assignment import AssignmentSearchListForm


class AssignmentStepListView(
        ProjectPermissionMixin,
        ListView
):

    model = AssignmentStep
    paginate_by = 30
    template_name = 'assignment/project/assigment_steps_list.html'
    filter_form_class = AssignmentSearchListForm

    def get_queryset(self, queryset=None):
        return self.model.objects.filter_by_project(self.get_project()).order_by('step__index')
