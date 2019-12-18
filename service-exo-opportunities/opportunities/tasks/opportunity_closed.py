import celery
import logging

from django.contrib.auth import get_user_model

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.mails.handlers import mail_handler

from ..mails import ApplicantNotSelected
from ..models import Opportunity
from ..conf import settings


User = get_user_model()
logger = logging.getLogger('celery-task')


class OpportunityClosedTask(celery.Task):
    name = 'Opportunity closed'

    def run(self, *args, **kwargs):
        opportunity_pk = kwargs.get('pk')
        user_pk = kwargs.get('user_pk')
        comment = kwargs.get('comment')
        email_name = settings.OPPORTUNITIES_MAIL_VIEW_CLOSED_MANUALLY
        try:
            opp = Opportunity.objects.get(pk=opportunity_pk)
        except Opportunity.DoesNotExist:
            logger.error('Opportunity does not exist')
            raise Exception()
        try:
            user = User.objects.get(id=user_pk)
        except User.DoesNotExist:
            logger.error('User does not exist')
            raise Exception()

        user_wrapper = UserWrapper(user=user)
        try:
            data = ApplicantNotSelected(opp, user).get_data()
        except Exception as err:
            logger.error('Applicant not selected data exception: {}'.format(err))
            raise Exception()
        data['recipients'] = [user_wrapper.email]
        if comment is not None:
            data['comment'] = comment
        status = mail_handler.send_mail(
            template=email_name,
            **data)
        if not status:
            logger.error('Error sending email to: {}'.format(data))
            raise Exception()
