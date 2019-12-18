from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin

from utils.mixins import DeleteMessageMixin

from ..models import Partner
from ..forms import PartnerForm
from ..conf import settings


class PartnerCreateView(
        PermissionRequiredMixin,
        CreateView
):
    model = Partner
    permission_required = settings.PARTNER_FULL_ADD_PARTNER
    template_name = 'partner/partner_form.html'
    form_class = PartnerForm
    success_message = '%(name)s was created successfully'
    success_url = reverse_lazy('partner:list')
    raise_exception = True


class PartnerEditView(
        GuardianPermissionRequiredMixin,
        SuccessMessageMixin,
        UpdateView
):

    model = Partner
    template_name = 'partner/partner_form.html'
    form_class = PartnerForm
    permission_required = settings.PARTNER_FULL_EDIT_PARTNER
    return_404 = True
    success_message = '%(name)s was edited successfully'
    success_url = reverse_lazy('partner:list')


class PartnerDetailView(
        GuardianPermissionRequiredMixin,
        DetailView
):

    model = Partner
    template_name = 'partner/partner_detail.html'
    permission_required = settings.PARTNER_FULL_VIEW_PARTNER
    return_404 = True


class PartnerDeleteView(
        DeleteMessageMixin,
        PermissionRequiredMixin,
        DeleteView
):

    model = Partner
    permission_required = settings.PARTNER_FULL_REMOVE_PARTNER
    success_url = reverse_lazy('partner:list')
    delete_message = '%(name)s was removed successfully'
    raise_exception = True

    def get_delete_message(self):
        return self.delete_message % {'name': self.get_object().name}
