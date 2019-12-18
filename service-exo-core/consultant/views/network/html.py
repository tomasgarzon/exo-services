from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.list import ListView

from ...conf import settings
from ...models import Consultant


class ExportNetworkAsHTMLView(
        PermissionRequiredMixin,
        ListView
):
    permission_required = settings.CONSULTANT_FULL_PERMS_CONSULTANT_LIST_AND_EXPORT
    template_name = 'network/bio_packages.html'
    paginate_by = None
    queryset = Consultant.all_objects.all()
    raise_exception = True

    def get_queryset(self):
        consultant_ids = self.request.GET.get('consultants', '').split(',')
        return self.queryset.filter(pk__in=consultant_ids)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        fields = self.request.GET.get('fields', '').split(',')
        context['fields'] = fields
        return context
