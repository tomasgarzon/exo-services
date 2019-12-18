import logging

from celery import Task

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.core.exceptions import ObjectDoesNotExist

from sentry_sdk import capture_exception

from mail.helpers import get_curated_content
from mail.models import Message, MessageLog

logger = logging.getLogger('service')


class SendMailTask(Task):
    name = 'SendEmailTask'
    ignore_result = False

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        msg = 'SendMailTask.on_failure: {}-{}'.format(task_id, exc)
        logger.error(msg)
        super(SendMailTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def run(self, *args, **kwargs):
        message_pk = kwargs.get('pk', None)
        to_addresses = kwargs.get('to_addresses', [])
        is_manually_sent = kwargs.get('is_manually_sent', False)

        message = Message.objects.get(pk=message_pk)

        msg = 'SendMailTask: Trying to send {} to {}'.format(message_pk, to_addresses)
        logger.info(msg)

        if isinstance(to_addresses, str):
            to_addresses = to_addresses.split(',')

        email = EmailMessage(
            subject=message.subject,
            body=message.email.get('body'),
            from_email=settings.MAIL_FROM_EMAIL,
            to=to_addresses,
            bcc=None,
            reply_to=[settings.MAIL_REPLY_TO],
            connection=get_connection(backend=settings.MAILER_EMAIL_BACKEND))

        for attachment in message.email.get('attachments', []):
            curated_content = get_curated_content(attachment)
            try:
                email.attach(attachment[0], curated_content, attachment[2])
            except IndexError:
                email.attach(attachment[0], curated_content, attachment[1])

        try:
            if email is not None:

                try:
                    categories = message.category.split(',')
                    if is_manually_sent:
                        email.categories = ['{}_DEBUG'.format(c) for c in categories]
                    else:
                        email.categories = categories

                    email.content_subtype = 'html'
                    email.send()

                    msg = 'SendMailTask: Message {} sent to {}'.format(message_pk, to_addresses)
                    logger.info(msg)

                    MessageLog.objects.create(
                        action=settings.MAIL_LOG_ACTIONS_SENT,
                        email=message,
                        message='to: {}'.format(email.to))

                except Exception as err:
                    MessageLog.objects.create(
                        action=settings.MAIL_LOG_ACTIONS_FAILED,
                        email=message,
                        message=err)
                    msg = 'SendMailTask Exception: {} - {}'.format(err, message_pk)
                    logger.error(msg)
                    self.retry(
                        countdown=120, max_retries=20)
            else:
                msg = 'Message {} discarded due to failure in converting from DB. Added on {}'.format(
                    message_pk, message.created)
                logger.warning(msg)
                MessageLog.objects.create(
                    action=settings.MAIL_LOG_ACTIONS_FAILED,
                    email=message,
                    message=msg)

        except ObjectDoesNotExist:
            msg = 'SendMailTask Message.ObjectDoesNotExist: {}'.format(message_pk)
            logger.error(msg)
        except Exception as exc:
            msg = 'SendMailTaskException: {}: {}'.format(type(exc).__name__, exc.args)
            logger.error(msg)
            self.retry(countdown=120, max_retries=20)
            capture_exception(exc)
