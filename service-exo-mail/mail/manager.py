from django.db import models

from .models.message_log import MessageLog
from .conf import settings


class MessageManager(models.Manager):
    def create(self, subject, to_email, from_email, body,
               reply_to, cc, bcc, attachment, created=None, category=''):
        message = self.model()
        message.subject = subject
        message.from_email = from_email
        message.reply_to = reply_to or settings.MAIL_REPLY_TO
        message.to_email = ','.join(to_email)
        message.cc = ','.join(cc)
        message.bcc = ','.join(bcc)
        message.body = body
        message.category = category
        message.email = {
            'body': body,
            'attachments': attachment
        }

        message.save()

        # If created is explicitly set, override automatic value
        if created:
            message.created = created
            message.save(update_fields=['created'])

        MessageLog.objects.create(
            action=settings.MAIL_LOG_ACTIONS_STORED,
            email=message,
            created=message.created)

        return message
