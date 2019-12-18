from django.conf import settings


class ConsultantAccessMixin:

    @property
    def has_tos_invitations_pending(self):
        return self.user.invitations.filter(
            status=settings.INVITATION_STATUS_CH_PENDING,
            type=settings.INVITATION_TYPE_AGREEMENT,
        ).exists()

    def get_tos_invitation_pending(self):
        return self.user.invitations.filter(
            status=settings.INVITATION_STATUS_CH_PENDING,
            type=settings.INVITATION_TYPE_AGREEMENT,
        ).first()

    @property
    def can_access_to_dashboard(self):
        return\
            not self.has_tos_invitations_pending\
            and self.has_registration_process_finished
