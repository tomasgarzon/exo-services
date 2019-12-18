import requests
import logging
import json
from requests_toolbelt import MultipartEncoder
from django.conf import settings
from celery import Task
from celery import current_app as app

logger = logging.getLogger('mail')


class SendMailTask(Task):
    name = 'SendMailTask'

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
        if settings.POPULATOR_MODE:
            return
        # TO DO: Refactor with url manager
        url = self.get_root() + 'api/mail/'

        try:
            recipients = params.get('recipients', [])
            logger.info('SendMailTask.run: {}'.format(template))

            if len(recipients):
                params['recipients'] = recipients
                data = {
                    'template': template,
                    'params': params,
                    'domain': settings.DOMAIN_NAME,
                }
                fields = data.copy()
                fields['params'] = json.dumps(fields['params'])
                if attachments:
                    att = []
                    for attach in attachments:
                        att.append(
                            ('attachments',
                             (attach.get_filename(), attach.as_string()),
                             )
                        )
                    fields.update({'file': att[0][1]})
                m = MultipartEncoder(fields=fields)
                # Connect to service exo-mail
                logger.info('SendMailTask.run.requests.post: {}'.format(recipients))
                response = requests.post(
                    url,
                    data=m,
                    headers={'Content-Type': m.content_type})
                if not response.ok:
                    logger.error('Request not valid: {}'.format(response.content))
                    raise Exception('Response error')

                logger.info('SendMailTask done: {}'.format(recipients))

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
