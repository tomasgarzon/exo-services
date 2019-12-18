from actstream.actions import unfollow

from ...conf import settings
from ...signals_define import opportunity_post_selected
from ..applicant_sow import ApplicantSow


class ApplicationStatusMixin:

    def cancel(self, user_from):
        self.set_status(user_from, settings.OPPORTUNITIES_CH_APPLICANT_CANCELED)

    def activate(self, user, *args, **kwargs):
        self.set_status(user, settings.OPPORTUNITIES_CH_APPLICANT_ACCEPTED)
        self.set_scheduling(
            user_from=user,
            scheduling_message=kwargs.get('comment', None),
        )
        slots = kwargs.get('slots', [])
        self.clear_and_set_slots(user, slots)
        self.ticket.collaboratorprojectrequest._respond_accept_mail(self)

    def deactivate(self, user_from, description):
        self.set_status(user_from, settings.OPPORTUNITIES_CH_APPLICANT_DECLINED)
        self.set_response_message(description)

    def mark_as_selected(self, user_from, response_message=None, **kwargs):
        unfollow(self.user, self.opportunity)

        self.set_status(user_from, settings.OPPORTUNITIES_CH_APPLICANT_SELECTED)

        ApplicantSow.objects.get_or_create(
            applicant=self,
            **kwargs)
        opportunity_post_selected.send(
            sender=self.__class__,
            opportunity=self.opportunity,
            applicant=self,
        )
        if response_message:
            self.set_response_message(response_message)

    def mark_as_rejected(self, user_from, response_message=None):
        self.set_status(user_from, settings.OPPORTUNITIES_CH_APPLICANT_REJECTED)

        if hasattr(self, 'sow'):
            self.sow.delete()

        if response_message:
            self.set_response_message(response_message)

    def mark_as_rejected_by_deadline(self):
        self.set_status(None, settings.OPPORTUNITIES_CH_APPLICANT_REJECTED)

        if hasattr(self, 'sow'):
            self.sow.delete()

    def accept_request(self, user_from):
        self.set_status(
            user_from, settings.OPPORTUNITIES_CH_APPLICANT_ACCEPTED)
        invitation = self.invitations_related.get()
        invitation.set_status(
            user_from, settings.INVITATION_STATUS_CH_ACTIVE)

    def set_response_message(self, response_message):
        self.response_message = response_message
        self.save(update_fields=['response_message', 'modified'])

    def set_completed(self, user_from=None):
        self.set_status(
            user_from, settings.OPPORTUNITIES_CH_APPLICANT_COMPLETED)

    def set_feedback_expired(self, user_from=None):
        self.set_status(
            user_from, settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_READY)
