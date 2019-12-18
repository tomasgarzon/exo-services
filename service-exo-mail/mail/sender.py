from email.mime.base import MIMEBase
from smtplib import SMTPSenderRefused

from django.core.mail import EmailMessage

from .conf import settings


class CustomEmailMessage(EmailMessage):

    def send(self, fail_silently=False, notify_webhook=None):
        """Send the email message."""
        if not self.recipients():
            # Don't bother creating the network connection if there's nobody to
            # send to.
            return 0
        return self.get_connection(fail_silently).send_messages(
            [self],
            notify_webhook or False,
        )


def send_email(
        from_email=settings.MAIL_FROM_EMAIL,
        bcc=[],
        cc=[],
        to_email=[],
        subject='Subject',
        body='Body',
        files_attachment=[],
        reply=[settings.MAIL_REPLY_TO],
        category=None,
        notify_webhook=None):
    email_sent = None
    headers = {}
    if category:
        headers = {settings.MAIL_CATEGORY_HEADER_KEY: category}

    mail = CustomEmailMessage(
        subject=subject,
        bcc=bcc,
        cc=cc,
        body=body,
        from_email=from_email,
        to=to_email,
        reply_to=reply,
        headers=headers
    )

    mail.content_subtype = 'html'

    for file_tmp in files_attachment:
        if isinstance(file_tmp, MIMEBase):
            mail.attach(file_tmp)
        else:
            try:
                mail.attach(file_tmp.name, file_tmp.read(), file_tmp.content_type)
            except Exception as ex:  # noqa
                mail.attach_file(file_tmp)

    try:
        email_sent = mail.send(notify_webhook=notify_webhook)
    except SMTPSenderRefused:
        pass

    return email_sent
