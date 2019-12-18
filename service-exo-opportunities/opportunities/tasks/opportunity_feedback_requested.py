import celery
import logging

from django.conf import settings

from utils.mails.handlers import mail_handler
from auth_uuid.utils.user_wrapper import UserWrapper

from ..mails import OpportunityFeedback
from ..models import Opportunity, Applicant


logger = logging.getLogger('celery-task')

MAIL_VIEW_APPLICANT_REQUESTED_FEEDBACK = 'opportunity_applicant_leave_feedback'
MAIL_VIEW_REQUESTER_REQUESTED_FEEDBACK = 'opportunity_requester_leave_feedback'


class OpportunityFeedackRequestedTask(celery.Task):
    name = 'OpportunityFeedackRequestedTask'

    def send_to_requester(self, opportunity, applicant):
        user_wrapper = UserWrapper(user=opportunity.created_by)
        try:
            data = OpportunityFeedback(applicant).get_data()
        except Exception as err:
            logger.error('Opportunity Feedback data exception: {}'.format(err))
            raise Exception()
        data['recipients'] = [user_wrapper.email]
        data['public_url'] = settings.OPPORTUNITIES_FEEDBACK_ADMIN_URL.format(opportunity.pk)
        status = mail_handler.send_mail(
            template=MAIL_VIEW_REQUESTER_REQUESTED_FEEDBACK,
            **data)
        if not status:
            logger.error('Error sending email to: {}'.format(data))
            raise Exception()

    def send_to_applicant(self, opportunity, applicant):
        user_wrapper = UserWrapper(user=applicant.user)
        try:
            data = OpportunityFeedback(applicant).get_data()
        except Exception as err:
            logger.error('Opportunity Feedback data exception: {}'.format(err))
            raise Exception()
        data['recipients'] = [user_wrapper.email]
        data['public_url'] = settings.OPPORTUNITIES_FEEDBACK_URL.format(opportunity.pk)
        status = mail_handler.send_mail(
            template=MAIL_VIEW_APPLICANT_REQUESTED_FEEDBACK,
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
        applicant_pk = kwargs.get('applicant_pk')
        try:
            applicant = opp.applicants_info.get(pk=applicant_pk)
        except Applicant.DoesNotExist:
            logger.error('Applicant does not exist')
            raise Exception()

        self.send_to_requester(opp, applicant)
        self.send_to_applicant(opp, applicant)
