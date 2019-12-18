import logging
from utils.mails.handlers import mail_handler

from celery import Task

from django.conf import settings
from django.utils import translation

from ..models import SurveyFilled
from ..api.serializers.survey_filled import ResultSerializer


logger = logging.getLogger('celery-task')


class SurveyFilledTask(Task):
    name = 'SurveyFilledTask'

    def run(self, *args, **kwargs):
        survey_filled_pk = kwargs.get('pk')

        email_name = settings.SURVEY_RESULT_FOR_USER

        try:
            survey_filled = SurveyFilled.objects.get(pk=survey_filled_pk)
        except SurveyFilled.DoesNotExist:
            logger.error('SurveyFilled does not exist')
            raise Exception()
        translation.activate(survey_filled.language)

        results_data = ResultSerializer(survey_filled.results.all(), many=True).data

        data = {
            'name': survey_filled.name,
            'organization': survey_filled.organization,
            'total': survey_filled.total,
            'survey_name': survey_filled.survey.name,
            'public_url': '/',
            'recipients': [survey_filled.email],
            'results': results_data,
            'lang': survey_filled.language,
        }
        logger.info(data)
        status = mail_handler.send_mail(
            template=email_name,
            **data)
        if not status:
            logger.error('Error sending email to: {}'.format(data))
