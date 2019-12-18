from django.conf import settings
import binascii

from utils.tasks.service_mail import SendMailTask


class MailHandler:

    def send_mail(self, template=None, **kwargs):
        if not settings.POPULATOR_MODE:
            attachments = []
            for attach in kwargs.get('attachments', []):
                try:
                    name, content = attach
                except (ValueError, TypeError):
                    name = attach.get_filename()
                    content = attach.as_string()
                try:
                    new_content = (name, binascii.b2a_base64(content))
                except TypeError:
                    new_content = (name, content)
                attachments.append(new_content)
            kwargs['attachments'] = attachments
            SendMailTask().s(template=template, params=kwargs).apply_async()


mail_handler = MailHandler()
