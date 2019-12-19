import logging
import requests
import json

from django.conf import settings

from requests_toolbelt import MultipartEncoder

from .attachments import fix_attachments


logger = logging.getLogger('mails')


class MailHandler:
    def get_root(self):
        if settings.SERVICE_EXO_MAIL_HOST.startswith('http'):
            root = settings.SERVICE_EXO_MAIL_HOST + '/'
        else:
            root = settings.ROOT + settings.SERVICE_EXO_MAIL_HOST

        return root

    def send_mail(self, template=None, **kwargs):
        status = True
        url = self.get_root() + 'api/mail/'
        logger.info('SendMail.run: {}'.format(template))
        recipients = kwargs.get('recipients', [])
        attachments = kwargs.pop('attachments', None)
        attachments_parsed = kwargs.pop('attachments_parsed', False)

        if len(recipients):
            data = {
                'template': template,
                'params': kwargs,
                'domain': settings.DOMAIN_NAME,
            }
            # Connect to service exo-mail
            logger.info('SendMail.run.requests.post: {}'.format(recipients))
            fields = data.copy()
            fields['params'] = json.dumps(fields['params'])

            if attachments:
                attachments = fix_attachments(attachments)
                # TO DO: Attach not only the first
                if attachments_parsed:
                    name, content = attachments[0]
                    fields.update({'file': (name, content)})
                else:
                    att = []
                    for attach in attachments:
                        attach_tuple = ('attachments', attach,)
                        att.append(attach_tuple)

                    fields.update({'file': att[0][1]})

            m = MultipartEncoder(fields=fields)

            try:
                response = requests.post(
                    url,
                    data=m,
                    headers={'Content-Type': m.content_type})

                if not response.ok:
                    logger.error('requests.error {}'.format(response.content))
                    status = False
            except Exception as err:
                message = 'Exception: {}-{}'.format(err, url)
                logger.error(message)
                status = False
        return status


mail_handler = MailHandler()
