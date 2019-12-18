from utils.generic.list import ListFilterView
from project.views.mixin import ProjectPermissionMixin, ProjectQuerySetListView

from ..models import Validation
from ..forms.filter import ValidationSearchListForm


class ValidationListView(
        ProjectPermissionMixin,
        ProjectQuerySetListView,
        ListFilterView
):
    template_name = 'validation/list.html'
    model = Validation
    paginate_by = 10
    filter_form_class = ValidationSearchListForm
