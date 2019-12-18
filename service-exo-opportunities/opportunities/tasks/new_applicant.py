import celery
import logging

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.notifications import send_notifications
from utils.mails.handlers import mail_handler
from utils.mails.mixin import EmailMixin

from ..mails import NewApplicant
from ..models import Opportunity, Applicant
from ..conf import settings
from ..api.serializers.opportunity_detail import OpportunityApplicantSerializer


logger = logging.getLogger('celery-task')
Request = type('Request', (object,), {'user': None, 'view': {'action': ''}})


class NewApplicantTask(EmailMixin, celery.Task):
    name = 'New applicant'

    def send_notification(self, user, applicant):
        request = Request()
        request.user = user
        serializer = OpportunityApplicantSerializer(
            applicant,
            context={'request': request})
        data = serializer.data
        data['opportunity'] = applicant.opportunity.pk
        action = settings.OPPORTUNITIES_ACTION_NEW_APPLICANT
        send_notifications(action, user.uuid, data)

    def run(self, *args, **kwargs):
        opportunity_pk = kwargs.get('pk')
        applicant_pk = kwargs.get('applicant_pk')
        email_name = settings.OPPORTUNITIES_MAIL_VIEW_RESPOND_APPLICANT

        try:
            opp = Opportunity.objects.get(pk=opportunity_pk)
            opportunity_creator = UserWrapper(user=opp.created_by)

        except Opportunity.DoesNotExist as err:
            logger.error('Opportunity does not exist')
            raise err

        try:
            applicant = opp.applicants_info.get(pk=applicant_pk)
        except Applicant.DoesNotExist as err:
            logger.error('Applicant does not exist')
            raise err

        try:
            data = NewApplicant(applicant).get_data()
        except Exception as err:
            logger.error('New Applicant data exception: {}'.format(err))
            raise err

        data['recipients'] = [opportunity_creator.email]
        status = mail_handler.send_mail(
            template=email_name,
            **data)
        if not status:
            logger.error('Error sending email to: {}'.format(data))
            raise Exception('Error sending email to: {}'.format(data))

        try:
            self.send_notification(opportunity_creator, applicant)
        except Exception as err:
            logger.error('Send notification exception: {}'.format(err))
