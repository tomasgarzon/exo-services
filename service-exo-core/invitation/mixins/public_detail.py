from django.http import HttpResponseForbidden

from guardian.mixins import PermissionRequiredMixin

from ..models import Invitation


class PublicInvitationMixin(PermissionRequiredMixin):
    model = Invitation
    slug_field = 'hash'
    slug_url_kwarg = 'hash'
    return_404 = True

    @property
    def user(self):
        return self.get_object().user

    def check_permissions(self, request):
        invitation = self.get_object()
        allow = invitation.can_be_accepted(self.user)
        if not allow:
            return HttpResponseForbidden()


class PublicInvitationStepDoneMixin:

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        registration_process = self.user.registration_process
        if registration_process and not registration_process.current_step.is_declined:
            context['next_step_url'] = registration_process.get_next_step_public_url()

        return context
