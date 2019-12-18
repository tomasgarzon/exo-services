import requests
import logging
import json

from requests_toolbelt import MultipartEncoder
from service.celery import app

from django.conf import settings

from celery import Task


logger = logging.getLogger('mails')


class SendMailTask(Task):
    name = 'Send Email'
    ignore_result = False

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        msg = 'SendMailTask.on_failure: {}-{}'.format(task_id, exc)
        logger.error(msg)
        super(SendMailTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def get_root(self):
        root = settings.EXOLEVER_HOST + settings.SERVICE_EXO_MAIL_HOST

        return root

    def run(self, *args, **kwargs):
        template = kwargs.get('template')
        params = kwargs.get('params')
        attachments = params.pop('attachments', '')
        url = self.get_root() + settings.EMAIL_POST_URL

        try:
            logger.info('SendMailTask.run: {}'.format(template))
            data = {
                'template': template,
                'params': params,
                'domain': settings.DOMAIN_NAME,
            }
            fields = data.copy()
            fields['params'] = json.dumps(fields['params'])
            if attachments:
                fields.update(
                    {'file': (
                        attachments[0],
                        attachments[1].encode(settings.PAYMENTS_PDF_DECODE_ISO)
                    )})

            m = MultipartEncoder(fields=fields)

            logger.info('SendMailTask.run.requests.post: {}'.format(
                params['recipients'])
            )
            response = requests.post(
                url,
                data=m,
                headers={'Content-Type': m.content_type})

            if not response.ok:
                logger.error('Request not valid: {}'.format(response.content))
                raise Exception('Response error')

        except requests.Timeout as err:
            message = 'requests.Timeout: {}-{}'.format(err, url)
            logger.error(message)
            self.retry(countdown=2 ** self.request.retries, max_retries=20)

        except requests.RequestException as err:
            message = 'requests.RequestException: {}-{}'.format(err, url)
            logger.error(message)
            self.retry(countdown=2 ** self.request.retries, max_retries=20)

        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)
            self.retry(countdown=2 ** self.request.retries, max_retries=20)


app.tasks.register(SendMailTask())
