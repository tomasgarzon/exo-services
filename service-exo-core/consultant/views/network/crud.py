from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.shortcuts import redirect
from django.contrib import messages

from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin

from exo_accounts.utils.util import normalize_email
from utils.segment import SegmentAnalytics

from ...models import Consultant
from ...forms.consultant import ConsultantAddForm


class ConsultantDetailView(
        PermissionRequiredMixin,
        DetailView
):

    model = Consultant
    template_name = 'network/detail.html'
    permission_required = settings.CONSULTANT_FULL_PERMS_CONSULTANT_LIST_AND_EXPORT
    raise_exception = True

    def get_queryset(self):
        return self.model.all_objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        consultant = self.get_object()
        context['registration_steps'] = consultant.registration_process
        context['public_sites'] = settings.CONSULTANT_PUBLIC_SITES
        return context


class ConsultantAdd(
        PermissionRequiredMixin,
        SuccessMessageMixin,
        FormView
):
    """
    Create Consultant
    """
    success_message = 'Invitation to %(name)s sent successfully'
    template_name = 'network/consultant_form.html'
    permission_required = settings.CONSULTANT_FULL_PERMS_ADD_CONSULTANT
    model = Consultant
    form_class = ConsultantAddForm
    success_url = reverse_lazy('consultant:list')
    raise_exception = True

    def form_valid(self, form):
        skip_steps = []
        email = normalize_email(form.cleaned_data.get('email'))
        name = form.cleaned_data.get('name')
        custom_text = form.cleaned_data.get('custom_text')
        full_name = name
        short_name = name.split(' ')[0]

        consultant = self.model.objects.create_consultant(
            short_name=short_name,
            full_name=full_name,
            email=email,
            invite_user=self.request.user,
            registration_process=True,
            skip_steps=skip_steps,
            custom_text=custom_text,
            coins=form.cleaned_data.get('coins'),
            waiting_list=form.cleaned_data.get('waiting_list'),
        )

        SegmentAnalytics.event(
            user=consultant.user,
            category=settings.INSTRUMENTATION_ONBOARDING_CATEGORY,
            event=settings.INSTRUMENTATION_EVENT_STARTED,
            entry_point=settings.INSTRUMENTATION_USER_ENTRY_POINT_NETWORK,
        )

        return super().form_valid(form)


class ConsultantDisable(
        GuardianPermissionRequiredMixin,
        SuccessMessageMixin,
        SingleObjectMixin,
        View
):

    success_message = 'Consultant disabled successfully'
    permission_required = settings.CONSULTANT_PERMS_CONSULTANT_EDIT_PROFILE
    return_404 = True
    model = Consultant
    success_url = reverse_lazy('consultant:list')

    def get_queryset(self):
        return self.model.all_objects.all()

    def check_permissions(self, request):
        has_network_perms = request.user.has_perm(
            settings.CONSULTANT_FULL_PERMS_CONSULTANT_LIST_AND_EXPORT)
        if has_network_perms:
            return None
        return super().check_permissions(request)

    def get(self, request, pk):
        consultant = self.get_object()
        consultant.disable(request.user)
        message = self.get_success_message({})
        messages.success(self.request, message)
        self.success_url = request.META.get('HTTP_REFERER')
        return redirect(self.success_url)
