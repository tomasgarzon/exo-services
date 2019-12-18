import requests
import logging
import json
import binascii
from requests_toolbelt import MultipartEncoder

from django.conf import settings

from celery import Task

from ..mail.recipients_handler import recipients_handler

logger = logging.getLogger('mail')


class SendMailTask(Task):
    name = 'SendMailTask'
    ignore_result = False

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        msg = 'SendMailTask.on_failure: {}-{}'.format(task_id, exc)
        logger.error(msg)
        super(SendMailTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def get_root(self):
        return '{}{}'.format(
            settings.EXOLEVER_HOST,
            settings.SERVICE_EXO_MAIL_HOST)

    def get_config_param(self, template):
        # TO DO: Refactor with url manager
        url = self.get_root() + 'api/config/'
        data = {
            'template': template
        }
        headers = {'Content-type': 'application/json'}
        return requests.post(url, data=json.dumps(data), headers=headers)

    def run(self, *args, **kwargs):
        template = kwargs.get('template')
        params = kwargs.get('params')
        attachments = params.pop('attachments', '')
        attachments_parsed = params.pop('attachments_parsed', False)

        # TO DO: Refactor with url manager
        url = self.get_root() + 'api/mail/'

        try:
            # Get config param to clear recipients if needed
            config_param_response = self.get_config_param(template)
            if not config_param_response.ok:
                logger.error('Config param Request not valid: {}-{}'.format(
                    config_param_response.content, template))
                return

            config_param = config_param_response.json().get('config')
            recipients = params.get('recipients', [])
            recipients_clear = list(recipients_handler.clear_recipients(config_param, recipients))
            lang = recipients_handler.get_recipients_language(recipients_clear)
            logger.info('SendMailTask.run: {}'.format(template))

            if len(recipients_clear):
                params['recipients'] = recipients_clear
                data = {
                    'template': template,
                    'lang': lang,
                    'params': params,
                    'domain': settings.DOMAIN_NAME,
                }
                fields = data.copy()
                fields['params'] = json.dumps(fields['params'])

                if attachments:
                    # TO DO: Attach not only the first
                    if attachments_parsed:
                        name, content = attachments[0]
                        content = binascii.a2b_base64(content)
                        fields.update({'file': (name, content)})
                    else:
                        att = []
                        for attach in attachments:
                            name, content = attach
                            try:
                                content = binascii.a2b_base64(content)
                            except TypeError:
                                pass
                            new_attach = name, content
                            attach_tuple = ('attachments', new_attach,)
                            att.append(attach_tuple)

                        fields.update({'file': att[0][1]})

                m = MultipartEncoder(fields=fields)

                # Connect to service exo-mail
                logger.info('SendMailTask.run.requests.post: {}'.format(recipients_clear))
                response = requests.post(
                    url,
                    data=m,
                    headers={'Content-Type': m.content_type})

                if not response.ok:
                    logger.error('Request not valid: {}'.format(response.content))
                    raise Exception('Response error')

                logger.info('SendMailTask done: {}'.format(recipients_clear))

        except requests.Timeout as err:
            message = 'requests.Timeout: {}-{}'.format(err, url)
            logger.error(message)
            self.retry(countdown=10, max_retries=20)

        except requests.RequestException as err:
            message = 'requests.RequestException: {}-{}'.format(err, url)
            logger.error(message)
            self.retry(countdown=10, max_retries=20)
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)
            self.retry(countdown=10, max_retries=20)
