import celery
import logging
import requests

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.mails.handlers import mail_handler

from ..mails import ApplicantSelected
from ..models import Opportunity
from ..conf import settings

logger = logging.getLogger('celery-task')


class OpportunitySelectedTask(celery.Task):
    name = 'Opportunity assigned'

    def send_email(self, opportunity, applicant):
        email_name = settings.OPPORTUNITIES_MAIL_VIEW_APPLICANT_SELECTED
        user_wrapper = UserWrapper(user=applicant.user)

        try:
            data = ApplicantSelected(applicant).get_data()
        except Exception as err:
            logger.error('Applicant Selected data exception: {}'.format(err))
            raise Exception()
        data['recipients'] = [user_wrapper.email]
        status = mail_handler.send_mail(
            template=email_name,
            **data)
        if not status:
            logger.error('Error sending email to: {}'.format(data))
            raise Exception('Error sending email to: {}'.format(data))

    def _create_from_opportunity(self, opportunity, applicant, url):
        headers = {'USERNAME': settings.AUTH_SECRET_KEY}
        data = {
            'user': applicant.user.uuid.__str__(),
            'user_from': opportunity.created_by.uuid.__str__(),
            'opportunity_uuid': opportunity.uuid.__str__(),
            'exo_role': opportunity.exo_role.code
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            assert response.status_code == requests.codes.ok
        except AssertionError:
            message = 'Exception: {}-{}'.format(response.content, url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)
        except Exception as err:
            message = 'Exception: {}-{}'.format(err, url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)

    def create_user_project_role(self, opportunity, applicant):
        url = '{}{}api/project-opportunities/{}/add_from_opportunity/'.format(
            settings.EXOLEVER_HOST,
            settings.SERVICE_PROJECTS_HOST,
            opportunity.context_object_uuid)
        self._create_from_opportunity(opportunity, applicant, url)

    def create_participant(self, opportunity, applicant):
        url = '{}{}api/event/participants/{}/add_from_opportunity/'.format(
            settings.EXOLEVER_HOST,
            settings.SERVICE_EVENTS_HOST,
            opportunity.context_object_uuid)
        self._create_from_opportunity(opportunity, applicant, url)

    def run(self, *args, **kwargs):
        opportunity_pk = kwargs.get('pk')
        applicant_pk = kwargs.get('applicant_pk')
        try:
            opp = Opportunity.objects.get(pk=opportunity_pk)
        except Opportunity.DoesNotExist:
            logger.error('Opportunity does not exist')
            raise Exception()

        applicant = opp.applicants_info.get(pk=applicant_pk)
        self.send_email(opp, applicant)
        if opp.context_object_uuid:
            if opp.context_content_type == settings.OPPORTUNITIES_CH_CONTEXT_EVENT:
                self.create_participant(opp, applicant)
            elif opp.context_content_type == settings.OPPORTUNITIES_CH_CONTEXT_PROJECT:
                self.create_user_project_role(opp, applicant)
