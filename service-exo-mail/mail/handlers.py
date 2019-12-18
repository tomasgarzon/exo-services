import logging

from django.utils import translation

from utils.regex import camel_to_snake

logger = logging.getLogger('service')


class MailHandler:

    def __init__(self):
        self._registry = {}

    def register(self, mail_view):
        mail_instance = mail_view()
        mail_instance_name = camel_to_snake(mail_view.__name__,).replace('_mail_view', '')
        self._registry[mail_instance_name] = mail_instance

    def activate_language(self, lang):
        translation.activate(lang)

    def send_mail(self, domain, template, lang=None, **kwargs):
        if lang:
            self.activate_language(lang)

        if template in self._registry:
            logger.info('MailHandler.send_mail: {} - {}'.format(domain, template))
            mail_class = self._registry[template]
            kwargs['domain'] = domain
            kwargs['category'] = mail_class.section
            return mail_class.send_mail(**kwargs)
        else:
            logger.error('MailHandler.send_mail ({}) Template {} does not exists'.format(
                domain,
                template,
            ))


mail_handler = MailHandler()
