from django.core.exceptions import ValidationError
from django.utils import timezone

from actstream.actions import follow
from actstream.models import followers

from ...conf import settings
from ...signals_define import (
    opportunity_post_removed,
    opportunity_post_send,
    opportunity_post_closed,
    signal_create_new_conversation,
    opportunity_deadline,
    send_message_to_conversation,
)


class OpportunityActionsMixin:

    def create_open_applicant(
            self, user_from, user,
            summary=None, questions_extra_info=None,
            answers=[], budget=None):

        self.can_apply(user)
        applicant = self.applicants_info.create_open_applicant(
            user_from=user_from,
            user=user,
            opportunity=self,
            summary=summary,
            questions_extra_info=questions_extra_info,
            budget=budget,
            answers=answers
        )
        return applicant

    def _remove_logical(self, user_from, comment=None):
        self.status = (user_from, settings.OPPORTUNITIES_CH_REMOVED)

        opportunity_post_removed.send(
            sender=self.__class__,
            opportunity=self, comment=comment or ''
        )
        for app in self.applicants_info.all():
            app.set_status(
                user_from,
                settings.OPPORTUNITIES_CH_APPLICANT_REMOVED)

    def remove(self, user_from, comment=None):
        self._remove_logical(user_from, comment)

    def can_do_actions(self, user_from, action, raise_exception=True):
        try:
            actions = self.user_actions(user_from)
        except TypeError as e:
            if raise_exception:
                raise e
            else:
                return True
        if action in actions:
            return True
        if raise_exception:
            raise ValidationError('Action {} not allowed for {}'.format(
                action, user_from.uuid))
        return False

    def send(self, user_from, raise_exception=True):
        self.can_do_actions(
            user_from, settings.OPPORTUNITIES_ACTION_CH_SEND,
            raise_exception=raise_exception)
        self.status = (user_from, settings.OPPORTUNITIES_CH_REQUESTED)
        opportunity_post_send.send(
            sender=self.__class__, opportunity=self,
        )
        if self.deadline_date:
            opportunity_deadline.send(
                sender=self.__class__,
                opportunity=self,
                deadline_date=self.deadline_date)

    def assign(self, user_from, applicant, response_message=None, **kwargs):
        applicant.can_do_actions(
            user_from, settings.OPPORTUNITIES_ACTION_CH_ASSIGN)
        applicant.mark_as_selected(user_from, response_message, **kwargs)

        send_message_to_conversation.send(
            sender=applicant.__class__,
            applicant=applicant,
            user_from=user_from,
            message=response_message)

    def reject(self, user_from, applicant, response_message=None):
        was_selected = applicant.is_selected
        applicant.can_do_actions(
            user_from, settings.OPPORTUNITIES_ACTION_CH_REJECT)
        applicant.mark_as_rejected(user_from, response_message)
        has_to_re_open = was_selected and\
            self.is_closed and\
            timezone.now().date() < self.deadline_date
        if has_to_re_open:
            self.status = (user_from, settings.OPPORTUNITIES_CH_REQUESTED)

    def close(self, user_from, comment=None):
        self.can_do_actions(user_from, settings.OPPORTUNITIES_ACTION_CH_CLOSE)
        self.status = (user_from, settings.OPPORTUNITIES_CH_CLOSED)
        user_list = followers(self)

        applicants = self.applicants_info.pending_applicants()
        for applicant in applicants:
            applicant.mark_as_rejected(user_from)

        opportunity_post_closed.send(
            sender=self.__class__, opportunity=self,
            user_list=user_list,
            origin=settings.OPPORTUNITIES_CH_CLOSE_MANUALLY,
            comment=comment)

    def close_by_deadline(self):
        self.status = (None, settings.OPPORTUNITIES_CH_CLOSED)
        history = self.history.last()
        history.description = 'Closed by deadline'
        history.save()
        applicants = self.applicants_info.pending_applicants()
        for applicant in applicants:
            applicant.mark_as_rejected_by_deadline()
        opportunity_post_closed.send(
            sender=self.__class__, opportunity=self,
            user_list=followers(self),
            origin=settings.OPPORTUNITIES_CH_CLOSE_DEADLINE)

    def close_by_positions_covered(self):
        self.status = (None, settings.OPPORTUNITIES_CH_CLOSED)
        history = self.history.last()
        history.description = 'Closed by positions covered'
        history.save()
        applicants = self.applicants_info.pending_applicants()
        for applicant in applicants:
            applicant.mark_as_rejected_by_deadline()
        opportunity_post_closed.send(
            sender=self.__class__, opportunity=self,
            user_list=followers(self),
            origin=settings.OPPORTUNITIES_CH_CLOSE_POSITIONS)

    def start_conversation(self, user_from, message, files, user_to=None):
        follow(user_from, self)
        signal_create_new_conversation.send(
            sender=self.__class__,
            opportunity=self,
            user_from=user_from,
            message=message,
            files=files,
            user_to=user_to,
        )

    def re_open(self, user_from, deadline_date):
        self.status = (user_from, settings.OPPORTUNITIES_CH_REQUESTED)
        self.deadline_date = deadline_date
        self.save()
