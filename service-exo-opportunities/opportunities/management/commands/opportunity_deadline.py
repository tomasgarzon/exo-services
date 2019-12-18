import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.mails.handlers import mail_handler

from ...mails.opportunity import OpportunityCloseReminder
from ...models import Opportunity


logger = logging.getLogger('service')
EMAIL_NAME = settings.OPPORTUNITIES_MAIL_VIEW_CLOSE_REMINDER


class Command(BaseCommand):
    help = (
        'Opportunities deadline'
    )

    def send_reminder_requester(self, opportunity, days):
        user_wrapper = UserWrapper(user=opportunity.created_by)
        try:
            data = OpportunityCloseReminder(opportunity).get_data()
        except Exception as err:
            logger.error('Applicant not selected data exception: {}'.format(err))
            raise Exception()

        duedate_timedelta = days
        data['duedate_timedelta'] = duedate_timedelta
        data['subject_args'] = {
            'duedate_timedelta': days,
        }
        data['recipients'] = [user_wrapper.email]
        if settings.TEST_MODE:
            self.stdout.write('{}'.format(data))
        if settings.POPULATOR_MODE:
            return
        status = mail_handler.send_mail(
            template=EMAIL_NAME,
            **data)

        if not status:
            logger.error('Error sending email to: {}'.format(data))
            raise Exception()

    def close_opportunity_by_deadline(self):
        opportunities = Opportunity.objects.filter(
            deadline_date__lte=timezone.now().date()).filter_by__status_requested()
        for opp in opportunities:
            opp.close_by_deadline()

    def reminder_opportunity_close(self, reminder):
        days, deadline_timedelta = reminder
        timedelta_diff = timedelta(days=days)
        opportunities = Opportunity.objects.filter(
            deadline_date=(timezone.now() + timedelta_diff).date()).filter_by__status_requested()
        for opp in opportunities:
            self.send_reminder_requester(opp, deadline_timedelta)

    def handle(self, *args, **options):
        self.stdout.write('Close opportunities by deadline and reminder:')
        self.close_opportunity_by_deadline()
        for reminder in settings.OPPORTUNITIES_DEADLINE_REMINDER:
            self.reminder_opportunity_close(reminder)
        self.stdout.write('Finish!!')
