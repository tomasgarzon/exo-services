from django.contrib.auth.mixins import PermissionRequiredMixin

from utils.generic.list import ListFilterView

from ..models import Customer
from ..conf import settings
from ..forms import CustomerListForm


class CustomerListView(PermissionRequiredMixin, ListFilterView):
    model = Customer
    permission_required = settings.CUSTOMER_FULL_LIST_CUSTOMER
    paginate_by = 10
    template_name = 'customer/list.html'
    filter_form_class = CustomerListForm
    raise_exception = True

    def get_queryset(self):
        queryset = self.model.objects.filter_by_user(
            self.request.user,
        ).filter_no_partners()
        self.form_filter.is_valid()
        data = self.form_filter.cleaned_data
        queryset = queryset.filter_complex(*data, **data)
        return queryset
