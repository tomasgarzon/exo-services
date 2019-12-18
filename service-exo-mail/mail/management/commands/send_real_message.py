from django.core.management.base import BaseCommand
import smtplib

from django.conf import settings
from django.core.mail import get_connection

from socket import error as socket_error

from mailer.models import Message


class Command(BaseCommand):
    help = 'Send real email'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('pk', nargs='+', type=int)
        parser.add_argument('to_addresses', nargs='+', type=str)

    def handle(self, *args, **options):
        message_pk = options.get('pk')[0]
        message = Message.objects.get(pk=message_pk)
        to_addresses = options.get('to_addresses')[0]

        email = message.email

        if email is not None:

            try:
                connection = get_connection(backend=settings.MAILER_EMAIL_BACKEND)

                email.to = [to_addresses]
                email.cc = []
                email.bcc = []
                email.reply_to = []
                email.connection = connection

                if not hasattr(email, 'reply_to'):
                    email.reply_to = []
                email.categories = ['tickets']
                email.send()
            except (
                socket_error, smtplib.SMTPSenderRefused,
                smtplib.SMTPRecipientsRefused,
                smtplib.SMTPDataError,
                smtplib.SMTPAuthenticationError,
            ) as err:
                # Get new connection, it case the connection itself has an error.
                connection = None
                msg = 'SendMailConsumerException: {} - {}'.format(err, message_pk)
                self.stdout.write(self.style.SUCCESS(msg))
