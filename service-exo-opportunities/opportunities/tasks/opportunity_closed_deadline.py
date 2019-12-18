import celery
import logging

from django.conf import settings

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.mails.handlers import mail_handler

from ..mails import OpportunityClosed
from ..models import Opportunity


logger = logging.getLogger('celery-task')

MAIL_VIEW_CLOSED_DEADLINE = 'opportunity_closed_by_deadline_requester'


class OpportunityClosedDeadlineTask(celery.Task):
    name = 'Opportunity closed by deadline'

    def run(self, *args, **kwargs):
        opportunity_pk = kwargs.get('pk')
        email_name = MAIL_VIEW_CLOSED_DEADLINE
        try:
            opp = Opportunity.objects.get(pk=opportunity_pk)
        except Opportunity.DoesNotExist:
            logger.error('Opportunity does not exist')
            raise Exception()

        user_wrapper = UserWrapper(user=opp.created_by)
        try:
            data = OpportunityClosed(opp).get_data()
        except Exception as err:
            logger.error('Requester deadline data exception: {}'.format(err))
            raise Exception()
        data['recipients'] = [user_wrapper.email]
        data['public_url'] = settings.OPPORTUNITIES_PUBLIC_URL
        status = mail_handler.send_mail(
            template=email_name,
            **data)
        if not status:
            logger.error('Error sending email to: {}'.format(data))
            raise Exception()
