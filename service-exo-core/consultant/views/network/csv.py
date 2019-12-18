from django.views.generic import View
from django.http import HttpResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin

from consultant.tasks import (
    NetworkListReportTask, ContractingDataListReportTask,
    CertificationReportTask)

from .mixin import NetworkListFilterMixin
from ...conf import settings
from ...models import Consultant


class ExportNetworkMixin(
        PermissionRequiredMixin,
        NetworkListFilterMixin,
        MultipleObjectMixin,
        SuccessMessageMixin,
        FormMixin,
        View
):

    permission_required = settings.CONSULTANT_FULL_PERMS_CONSULTANT_LIST_AND_EXPORT
    paginate_by = None
    queryset = Consultant.all_objects.all()
    search_field = 'q'
    raise_exception = True
    success_url = reverse_lazy('consultant:list')
    success_message = 'Network report will be sent by email'

    def get_form_kwargs(self):
        kwargs = {'initial': self.get_initial()}

        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        return HttpResponse('Error')

    def form_valid(self, form):
        response = super().form_valid(form)

        queryparam = form.data.get('q', None)
        order_by = form.data.get('order_by', None)

        self.task_class().s(
            email_recipient=self.request.user.email,
            queryparam=queryparam,
            order_by=order_by).apply_async()

        return response


class ExportNetworkAsCSVView(ExportNetworkMixin):
    task_class = NetworkListReportTask


class ExportContractingDataAsCSVView(ExportNetworkMixin):
    task_class = ContractingDataListReportTask


class ExportCertificationAsCSVView(ExportNetworkMixin):
    task_class = CertificationReportTask
