from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages

from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin

from utils.mixins import DeleteMessageMixin

from ..models import Customer
from ..forms import CustomerForm
from ..conf import settings


class CustomerCreateView(
        PermissionRequiredMixin,
        CreateView
):
    model = Customer
    permission_required = settings.CUSTOMER_FULL_ADD_CUSTOMER
    template_name = 'customer/customer_form.html'
    form_class = CustomerForm
    success_message = '%(name)s was created successfully'
    raise_exception = True

    def form_valid(self, form):
        id_organization = form.cleaned_data.get('organization_id')
        self.object = form.save(commit=False)
        self.object._organization = id_organization
        self.object.save()
        partner = form.cleaned_data.get('partner')
        self.object.set_partner(partner)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('customer:list')

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data


class CustomerEditView(
        GuardianPermissionRequiredMixin,
        SuccessMessageMixin,
        UpdateView
):

    model = Customer
    template_name = 'customer/customer_form.html'
    form_class = CustomerForm
    permission_required = settings.CUSTOMER_FULL_EDIT_CUSTOMER
    return_404 = True
    success_message = '%(name)s was edited successfully'

    def get_initial(self):
        initial = super().get_initial()
        initial['is_training'] = self.object.training
        initial['partner'] = self.object.partners.first()
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        partner = form.cleaned_data.get('partner')
        self.object.set_partner(partner)
        return response

    def get_success_url(self):
        return reverse('customer:list')


class CustomerDetailView(
        GuardianPermissionRequiredMixin,
        DetailView
):

    model = Customer
    template_name = 'customer/customer_detail.html'
    permission_required = settings.CUSTOMER_FULL_VIEW_CUSTOMER
    return_404 = True


class CustomerDeleteView(
        DeleteMessageMixin,
        PermissionRequiredMixin,
        DeleteView
):

    model = Customer
    permission_required = settings.CUSTOMER_FULL_REMOVE_CUSTOMER
    success_url = reverse_lazy('customer:list')
    delete_message = '%(name)s was removed successfully'
    raise_exception = True

    def get_delete_message(self):
        return self.delete_message % {'name': self.get_object().name}
