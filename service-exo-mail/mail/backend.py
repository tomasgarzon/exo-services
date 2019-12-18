import logging
import requests

from django.urls import reverse

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

from .engine import send_email
from mail.models import Message

logger = logging.getLogger('mails')


def get_admins():
    return [mail for name, mail in settings.ADMINS]


class StoreBackend(BaseEmailBackend):
    def __get_category_from_header(self, email):
        category = None
        if settings.MAIL_CATEGORY_HEADER_KEY in email.extra_headers:
            category = email.extra_headers.get(settings.MAIL_CATEGORY_HEADER_KEY, None)
            email.extra_headers.pop(settings.MAIL_CATEGORY_HEADER_KEY)
        return category

    def __is_error_or_test_mail(self, subject):
        return subject.startswith(settings.MAIL_ERROR_MESAGE_SUBJECT) or subject.startswith(
            settings.MAIL_TEST_MESSAGE_SUBJECT)

    def send_messages(self, email_messages, notify_webhook=None):
        AUTOSEND = getattr(settings, 'MAILER_AUTOSEND', False)
        num_sent = 0

        for email in email_messages:
            if self.__is_error_or_test_mail(email.subject):
                email.to = get_admins()
                email.connection = get_connection(
                    backend=settings.MAILER_EMAIL_BACKEND
                )
                email.send()
            else:
                msg = Message.objects.create(
                    subject=email.subject,
                    to_email=email.to,
                    from_email=email.from_email,
                    reply_to=email.reply_to,
                    cc=email.cc,
                    bcc=email.bcc,
                    body=email.body,
                    category=self.__get_category_from_header(email),
                    attachment=email.attachments)

                if notify_webhook:
                    mail_url = '{}{}'.format(
                        settings.DOMAIN_NAME,
                        reverse('mail:inbox-message', kwargs={'pk': msg.pk}),
                    )
                    try:
                        requests.put(
                            notify_webhook,
                            data={
                                'email_url': mail_url,
                                'email_status': settings.MAIL_NOTIFY_WEBHOOK_STATUS_OK,
                            },
                        )
                    except Exception as e:  # noqa
                        logger.error('Notify webhook Exception: {}'.format(e))

                if AUTOSEND:
                    send_email(msg)

            num_sent += 1

        return num_sent
