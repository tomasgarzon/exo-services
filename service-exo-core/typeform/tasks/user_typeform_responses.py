from django.conf import settings
from django.urls import reverse

from celery import Task

from utils.mail import handlers


class NewUserTypeformResponseMailTask(Task):
    name = 'NewUserTypeformResponseMailTask'
    ignore_result = True

    def run(self, user_response_uuid, username, response_related, user_response, *args, **kwargs):
        email_recipients = settings.TYPEFORMFEEDBACK_NOTIFY_EMAILS_LIST

        url = reverse(
            'typeform:typeform_feedback:validate',
            kwargs={'uuid': user_response_uuid}
        )
        kwargs = {
            'username': username,
            'response_related': response_related,
            'user_response': user_response,
            'public_url': '{}{}'.format(settings.ROOT, url),
        }

        handlers.mail_handler.send_mail(
            'typeform_new_response',
            recipients=email_recipients,
            **kwargs)
