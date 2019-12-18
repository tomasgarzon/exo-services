import logging
import io
import csv

from django.core.management.base import BaseCommand
from django.db.models import F, Q
from django.utils import timezone
from django.conf import settings

from auth_uuid.utils.user_wrapper import UserWrapper
from utils.mails.handlers import mail_handler

from ...models import Applicant

logger = logging.getLogger('service')


class Command(BaseCommand):
    help = (
        'Opportunities dialy report for finance'
    )

    def get_file(self, applicants):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Title', 'Role', 'ID', 'Created by',
            'Applicant Selected', 'Opportunity Status',
            'Applicant status'])
        for app in applicants:
            opportunity = app.opportunity
            created = UserWrapper(user=opportunity.created_by).get_full_name()
            applicant = UserWrapper(user=app.user).get_full_name()
            writer.writerow([
                opportunity.title,
                opportunity.role_string,
                opportunity.id,
                created,
                applicant,
                opportunity.get_status_display(),
                app.get_status_display()])
        return output.getvalue()

    def send_summary(self, applicants):
        recipients = ['finance@openexo.com']
        email_name = 'basic_email'

        date = timezone.now().strftime('%Y-%m-%d_%H:%M:%S')
        file = ['report-{}.csv'.format(date), self.get_file(applicants)]
        kwargs = {
            'mail_title': 'Opportunities report',
            'mail_content': 'Date - {}'.format(date),
            'attachments': [file],
            'attachments_parsed': True,
        }

        status = mail_handler.send_mail(
            template=email_name,
            recipients=recipients,
            **kwargs)

        if not status:
            logger.error('Error sending email to finance')
            raise Exception()

    def get_applicants_feedback_received(self):
        q1 = Q(
            feedbacks__created_by=F('opportunity__created_by'),
            feedbacks__created__date=timezone.now().date())
        q2 = ~Q(feedbacks__created_by=F('opportunity__created_by')) &\
            Q(history__created__date=timezone.now().date(),
                history__status=settings.OPPORTUNITIES_CH_APPLICANT_FEEDBACK_READY)
        return Applicant.objects.filter(q1 | q2).distinct()

    def handle(self, *args, **options):
        self.stdout.write('Send opportunities confirmed:')
        applicants = self.get_applicants_feedback_received()
        if applicants.count() > 0:
            self.send_summary(applicants)
        total = applicants.count()
        self.stdout.write('Total: {}'.format(total))
        self.stdout.write('Finish!!')
