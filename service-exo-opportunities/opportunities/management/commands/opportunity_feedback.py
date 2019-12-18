import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...tasks import (
    OpportunityFeedackRequestedTask,
    OpportunityFeedackReminderRequesterTask,
    OpportunityFeedackReminderApplicantTask,
    OpportunityFeedackExpiredRequesterTask,
    OpportunityFeedackExpiredApplicantTask)
from ...models import Applicant


logger = logging.getLogger('service')


class Command(BaseCommand):
    help = (
        'Opportunities complete'
    )

    def complete_applicant_by_end_date(self):
        applicants = Applicant.objects.filter(
            sow__end_date=timezone.now().date()).filter_by_status_selected()
        for app in applicants:
            self.stdout.write('Completed: {}'.format(app.pk))
            app.set_completed()
            OpportunityFeedackRequestedTask().s(
                pk=app.opportunity.pk,
                applicant_pk=app.pk).apply_async()

    def feedback_reminder(self):
        days_2_before = timezone.now() - timedelta(days=2)
        applicants = Applicant.objects.filter(
            sow__end_date=days_2_before.date())
        for app in applicants:
            if app.is_completed or app.is_feedback_applicant_received:
                self.stdout.write('Requester reminder: {}'.format(app.pk))
                OpportunityFeedackReminderRequesterTask().s(
                    pk=app.opportunity.pk,
                    applicant_pk=app.pk).apply_async()
            if app.is_completed or app.is_feedback_requester_received:
                self.stdout.write('Applicant reminder: {}'.format(app.pk))
                OpportunityFeedackReminderApplicantTask().s(
                    pk=app.opportunity.pk,
                    applicant_pk=app.pk).apply_async()

    def feedback_expired(self):
        days_7_before = timezone.now() - timedelta(days=7)
        applicants = Applicant.objects.filter(
            sow__end_date=days_7_before.date())
        for app in applicants:
            if app.is_completed or app.is_feedback_applicant_received:
                self.stdout.write('Requester expired: {}'.format(app.pk))
                OpportunityFeedackExpiredRequesterTask().s(
                    pk=app.opportunity.pk,
                    applicant_pk=app.pk).apply_async()
            if app.is_completed or app.is_feedback_requester_received:
                self.stdout.write('Applicant expired: {}'.format(app.pk))
                OpportunityFeedackExpiredApplicantTask().s(
                    pk=app.opportunity.pk,
                    applicant_pk=app.pk).apply_async()

    def handle(self, *args, **options):
        self.complete_applicant_by_end_date()
        self.feedback_reminder()
        self.feedback_expired()
