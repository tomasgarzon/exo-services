from django.conf import settings

from utils.tasks import SendMailTask


class MailHandler:

    def send_mail(self, template=None, **kwargs):
        if settings.POPULATOR_MODE:
            return
        SendMailTask().s(template=template, params=kwargs).apply_async()


mail_handler = MailHandler()
