import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Sum, F
from django.utils import timezone

from utils.mails.handlers import mail_handler

from ...models import Opportunity
from ...recipients_helper import _get_recipients

logger = logging.getLogger('service')
EMAIL_NAME_SIGNED = settings.OPPORTUNITIES_MAIL_VIEW_DAILY_SUMMARY_SIGNED
EMAIL_NAME_NOT_SIGNED = settings.OPPORTUNITIES_MAIL_VIEW_DAILY_SUMMARY_NOT_SIGNED


class Command(BaseCommand):
    help = ('Opportunities dialy summary')

    def get_data_signed(self, total, roles, opportunities):
        data = {
            'total': total,
            'roles': [],
            'public_url': settings.OPPORTUNITIES_PUBLIC_URL
        }
        roles_ordered = sorted(roles, key=lambda k: k['total'], reverse=True)
        total_shown = 0

        for role in roles_ordered[:2]:
            name = role['name']
            total_role = role['total']
            total_shown += total_role
            data_role = {
                'total': total_role,
                'name': name,
                'opportunities': []
            }

            for opp in opportunities.filter(exo_role__name=name):
                data_role['opportunities'].append({
                    'title': opp.title,
                    'description': opp.description,
                    'entity': opp.entity or '',
                    'deadline': opp.deadline_date.strftime('%d %B %Y'),
                    'url': opp.url_public})

            data['roles'].append(data_role)
        data['other_total'] = total - total_shown

        return data

    def get_data_not_signed(self, total, roles, opportunities):
        return {
            'total': total,
            'roles': list(roles),
            'public_url': settings.OPPORTUNITIES_PUBLIC_URL
        }

    def send_summary(self, total, roles, opportunities):
        recipients = _get_recipients()

        data_not_signed = self.get_data_not_signed(total, roles, opportunities)
        data_signed = self.get_data_signed(total, roles, opportunities)

        for recipient in recipients:
            if recipient.get('has_signed_marketplace_agreement', True):
                email_name = EMAIL_NAME_SIGNED
                data = data_signed.copy()
            else:
                email_name = EMAIL_NAME_NOT_SIGNED
                data = data_not_signed.copy()

            data['name'] = recipient.get('short_name')
            data['subject_args'] = {'total': str(total)}
            status = mail_handler.send_mail(
                template=email_name,
                recipients=[recipient.get('email')],
                **data)

            if not status:
                logger.error('Error sending email to: {}'.format(data))
                raise Exception()

    def get_opportunities_open_and_not_sent(self):
        opportunities = Opportunity.objects.filter(
            sent_at__isnull=True,
            target=settings.OPPORTUNITIES_CH_TARGET_OPEN,
        ).filter_by__status_requested()
        total = opportunities.aggregate(total=Sum('num_positions'))['total'] or 0
        roles = opportunities.exclude(
            exo_role__isnull=True).values('exo_role__name').order_by('exo_role__name').annotate(
            total=Sum('num_positions'), name=F('exo_role__name'))

        return total, roles, opportunities

    def update_sent(self, opportunities):
        opportunities.update(sent_at=timezone.now())

    def handle(self, *args, **options):
        self.stdout.write('Send new opportunities summary:')
        total, roles, opportunities = self.get_opportunities_open_and_not_sent()

        if total > 0:
            self.send_summary(total, roles, opportunities)
            self.update_sent(opportunities)

        self.stdout.write('Total: {}'.format(total))
        self.stdout.write('Finish!!')
