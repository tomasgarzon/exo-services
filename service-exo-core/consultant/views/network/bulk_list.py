from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin

from utils.generic.list import ListFilterView

from ...models import BulkCreation
from ...forms.filters import BulkCreationDetailForm, BulkCreationListForm


class BulkCreationListView(
        PermissionRequiredMixin,
        ListFilterView
):

    model = BulkCreation
    paginate_by = 20
    template_name = 'network/bulk_creation_list.html'
    filter_form_class = BulkCreationListForm
    _suffix_list = 'list'
    permission_required = settings.CONSULTANT_FULL_PERMS_CONSULTANT_LIST_AND_EXPORT
    raise_exception = True

    def get_base_queryset(self):
        return self.model.objects.all()

    def get_queryset(self):
        queryset = self.get_base_queryset()
        self.form_filter.is_valid()
        data = self.form_filter.cleaned_data
        queryset = queryset.filter_complex(*data, **data)
        return queryset


class BulkCreationConsultantDetailView(
        PermissionRequiredMixin,
        ListFilterView
):

    model = BulkCreation
    template_name = 'network/bulk_creation_detail.html'
    paginate_by = 100
    permission_required = settings.CONSULTANT_FULL_PERMS_ADD_CONSULTANT
    filter_form_class = BulkCreationDetailForm
    raise_exception = True

    def get_object(self):
        return BulkCreation.objects.get(id=self.kwargs.get('pk'))

    def get_queryset(self):
        bulk_creation = self.get_object()
        self.form_filter.is_valid()
        data = self.form_filter.cleaned_data
        queryset = bulk_creation.consultants.all().filter_complex(*data, **data)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['bulk_creation'] = self.get_object()
        return context
