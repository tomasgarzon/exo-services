from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, FormView

from .mixin import NetworkListFilterMixin
from ...conf import settings
from ...models import Consultant
from ...search.helpers import get_filtered_data


class NetworkListView(
        PermissionRequiredMixin,
        NetworkListFilterMixin,
        ListView,
        FormView):
    permission_required = settings.CONSULTANT_FULL_PERMS_CONSULTANT_LIST_AND_EXPORT
    template_name = 'network/list.html'
    form_name = 'form_filter'
    queryset = Consultant.all_objects.all()
    paginate_by = 15
    raise_exception = True

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super().get_form_kwargs()
        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context

    def get_queryset(self):
        pattern = self.request.GET.get('q', None)
        order_by = self.request.GET.get('order_by', None)

        self.queryset = get_filtered_data(
            self.queryset,
            pattern,
            order_by)

        return super().get_queryset()
