import celery
import logging

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.mails.handlers import mail_handler

from ..mails import OpportunityClosed
from ..models import Opportunity
from ..conf import settings

logger = logging.getLogger('celery-task')


class OpportunityClosedByPositionTask(celery.Task):
    name = 'Opportunity has been closed because the positions are covered'

    def send_mail_to_requester(self, opportunity):
        email_name = settings.OPPORTUNITIES_MAIL_VIEW_CLOSED_BY_POSITIONS
        try:
            data = OpportunityClosed(opportunity).get_data()
        except Exception as err:
            logger.error('Opportunity closed selected data exception: {}'.format(err))
            raise Exception()
        user_wrapper = UserWrapper(user=opportunity.created_by)
        data['recipients'] = [user_wrapper.email]
        status = mail_handler.send_mail(
            template=email_name,
            **data)
        if not status:
            logger.error('Error sending email to: {}'.format(data))
            raise Exception()

    def run(self, *args, **kwargs):
        opportunity_pk = kwargs.get('pk')

        try:
            opp = Opportunity.objects.get(pk=opportunity_pk)
        except Opportunity.DoesNotExist:
            logger.error('Opportunity does not exist')
            raise Exception()

        self.send_mail_to_requester(opp)
