from django.contrib.auth.mixins import LoginRequiredMixin

from utils.generic.list import ListFilterView

from ..models import Project
from ..forms import ProjectListForm

from .mixin_public_object_names import PublicObjectNamesMixin


class ProjectListView(
    LoginRequiredMixin,
    PublicObjectNamesMixin,
    ListFilterView
):

    model = Project
    paginate_by = 20
    template_name = 'project/list.html'
    filter_form_class = ProjectListForm
    _suffix_list = 'list'

    def get_base_queryset(self):
        return self.model.objects.filter_by_user(self.request.user)

    def get_queryset(self):
        queryset = self.get_base_queryset()
        self.form_filter.is_valid()
        data = self.form_filter.cleaned_data
        queryset = queryset.filter_complex(*data, **data)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['url_list'] = 'project:service-list'

        return context
