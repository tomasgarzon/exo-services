from django.db import models
from django.core.exceptions import ValidationError

from model_utils.models import TimeStampedModel

from utils.descriptors import ChoicesDescriptorMixin

from ..conf import settings
from ..manager.applicant import ApplicantManager
from ..signals_define import opportunity_feedback_left
from .mixins import (
    ApplicationStatusMixin,
    ApplicationInvitationMixin,
    ApplicantCalendarMixin,
)


class Applicant(
        ApplicationStatusMixin,
        ApplicationInvitationMixin,
        ApplicantCalendarMixin,
        ChoicesDescriptorMixin,
        TimeStampedModel
):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='opp_applicants_info',
        on_delete=models.CASCADE,
    )
    opportunity = models.ForeignKey(
        'Opportunity', related_name='applicants_info',
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=1,
        choices=settings.OPPORTUNITIES_CH_APPLICANT_STATUS,
        default=settings.OPPORTUNITIES_CH_APPLICANT_DRAFT,
    )
    summary = models.TextField(blank=True, null=True)
    questions_extra_info = models.TextField(blank=True, null=True)
    budget = models.CharField(
        max_length=200,
        blank=True, null=True)
    response_message = models.TextField(blank=True, null=True)

    objects = ApplicantManager()

    def __str__(self):
        return '{} - {}: {}'.format(
            self.user, self.opportunity,
            self.get_status_display(),
        )

    def set_status(self, user_from, new_status):
        self.status = new_status
        self.save(update_fields=['status', 'modified'])
        self.history.create(
            status=new_status,
            user=user_from)

    def send(self, user_from):
        self.set_status(user_from, settings.OPPORTUNITIES_CH_APPLICANT_PENDING)

    def set_requested(self, user_from):
        self.set_status(user_from, settings.OPPORTUNITIES_CH_APPLICANT_REQUESTED)

    @property
    def selected_by(self):
        try:
            return self.history.filter(
                status=settings.OPPORTUNITIES_CH_APPLICANT_SELECTED).first().user
        except AttributeError:
            return None

    def user_actions(self, user_from):
        if self.user == user_from:
            if self.is_completed or self.is_feedback_requester_received:
                return [settings.OPPORTUNITIES_ACTION_CH_FEEDBACK]
            return []
        else:
            admin_perms = user_from in self.opportunity.admin_users
            if not admin_perms:
                return []
            if self.opportunity.is_removed:
                return []
            if self.is_requested:
                return [
                    settings.OPPORTUNITIES_ACTION_CH_ASSIGN,
                    settings.OPPORTUNITIES_ACTION_CH_REJECT]
            elif self.is_selected:
                return [
                    settings.OPPORTUNITIES_ACTION_CH_REJECT,
                    settings.OPPORTUNITIES_ACTION_CH_SOW_EDIT,
                ]
            elif self.is_rejected:
                return [
                    settings.OPPORTUNITIES_ACTION_CH_ASSIGN]
            elif self.is_completed or self.is_feedback_applicant_received:
                return [settings.OPPORTUNITIES_ACTION_CH_FEEDBACK]
            return []

    def can_do_actions(self, user_from, action, raise_exception=True):
        actions = self.user_actions(user_from)
        if action in actions:
            return True
        if raise_exception:
            raise ValidationError('Action {} not allowed for {}'.format(
                action, user_from.uuid))
        return False

    @property
    def has_sow(self):
        try:
            self.sow
        except AttributeError:
            return False
        else:
            return True

    def update_sow(self, user_from, **kwargs):
        self.can_do_actions(
            user_from, settings.OPPORTUNITIES_ACTION_CH_SOW_EDIT)
        try:
            applicant_sow = self.sow
        except AttributeError:
            return
        applicant_sow.update_sow(**kwargs)

    def give_feedback(self, user_from, **kwargs):
        self.can_do_actions(
            user_from, settings.OPPORTUNITIES_ACTION_CH_FEEDBACK)
        applicant_feedback = self.feedbacks.create(
            created_by=user_from,
            **kwargs)
        if self.is_completed:
            if user_from == self.user:
                self.set_status(user_from, settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_APP)
            else:
                self.set_status(user_from, settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_REQUESTER)
        else:
            self.set_status(user_from, settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_READY)
        opportunity_feedback_left.send(
            sender=self.__class__,
            opportunity=self.opportunity,
            applicant=self,
            user_from=user_from)
        return applicant_feedback

    @property
    def start_date_full(self):
        start_date_full = ''

        if self.has_sow:
            start_date_full = self.sow.start_date.strftime('%d %B %Y')
            if self.sow.start_time:
                start_date_full = '{} {}'.format(start_date_full, self.sow.start_time.strftime('%H:%-M %p'))
            if self.sow.timezone:
                start_date_full = '{} ({})'.format(start_date_full, self.sow.timezone_name.replace('/', ', '))

        return start_date_full

    @property
    def url(self):
        return settings.OPPORTUNITIES_APPLICANT_URL.format(self.opportunity.pk)
