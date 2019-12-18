import logging
import requests
import json

from django.conf import settings


logger = logging.getLogger('mails')


class MailHandler:
    def get_root(self):
        root = settings.EXOLEVER_HOST + settings.SERVICE_EXO_MAIL_HOST

        return root

    def send_mail(self, template=None, **kwargs):
        status = True
        kwargs.pop('attachments', None)
        url = self.get_root() + 'api/mail/'
        headers = {'Content-type': 'application/json'}
        logger.info('SendMail.run: {}'.format(template))
        recipients = kwargs.get('recipients', [])
        if len(recipients):
            data = {
                'template': template,
                'params': kwargs,
                'domain': settings.DOMAIN_NAME,
            }
            # Connect to service exo-mail
            logger.info('SendMail.run.requests.post: {}'.format(recipients))
            data['params'] = json.dumps(data['params'])
            try:
                response = requests.post(url, data=json.dumps(data), headers=headers)
                if not response.ok:
                    logger.error('requests.error {}'.format(response.content))
                    status = False
            except Exception as err:
                message = 'Exception: {}-{}'.format(err, url)
                logger.error(message)
                status = False
        return status


mail_handler = MailHandler()
