import celery
import logging

from django.contrib.auth import get_user_model

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.mails.handlers import mail_handler

from ..mails import ApplicantNotSelected
from ..models import Opportunity
from ..conf import settings

logger = logging.getLogger('celery-task')


class OpportunityNotSelectedTask(celery.Task):
    name = 'Opportunity people not assigned'

    def run(self, *args, **kwargs):
        opportunity_pk = kwargs.get('pk')
        user_pk = kwargs.get('user_pk')
        email_name = settings.OPPORTUNITIES_MAIL_VIEW_APPLICANT_NOT_SELECTED
        try:
            opp = Opportunity.objects.get(pk=opportunity_pk)
        except Opportunity.DoesNotExist:
            logger.error('Opportunity does not exist')
            raise Exception()
        try:
            user = get_user_model().objects.get(pk=user_pk)
        except get_user_model().DoesNotExist:
            logger.error('Applicant does not exist')
            raise Exception()

        user_wrapper = UserWrapper(user=user)
        try:
            data = ApplicantNotSelected(opp, user).get_data()
        except Exception as err:
            logger.error('Applicant not selected data exception: {}'.format(err))
            raise Exception()
        data['recipients'] = [user_wrapper.email]
        status = mail_handler.send_mail(
            template=email_name,
            **data)
        if not status:
            logger.error('Error sending email to: {}'.format(data))
            raise Exception()
