from django.contrib.auth.mixins import PermissionRequiredMixin

from utils.generic.list import ListFilterView

from ..models import Partner
from ..conf import settings
from ..forms import PartnerListForm


class PartnerListView(PermissionRequiredMixin, ListFilterView):
    model = Partner
    permission_required = settings.PARTNER_FULL_LIST_PARTNER
    paginate_by = 10
    template_name = 'partner/list.html'
    filter_form_class = PartnerListForm
    raise_exception = True

    def get_queryset(self):
        queryset = self.model.objects.filter_by_user(
            self.request.user,
        )
        self.form_filter.is_valid()
        data = self.form_filter.cleaned_data
        queryset = queryset.filter_complex(*data, **data)
        return queryset
