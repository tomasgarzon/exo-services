from django.core.management.base import BaseCommand

from mailer.models import Message


class Command(BaseCommand):
    help = 'Update server name in emails'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('from_server', nargs='+', type=str)
        parser.add_argument('to_server', nargs='+', type=str)

    def handle(self, *args, **options):
        from_server = options.get('from_server')[0]
        to_server = options.get('to_server')[0]
        found = 0

        self.stdout.write(self.style.SUCCESS('Changing from "{}" to "{}"'.format(from_server, to_server)))

        for message in Message.objects.all():
            email = message.email

            if from_server in email.body:
                email.body = email.body.replace(from_server, to_server)
                message.email = email
                message.save(update_fields=['message_data'])
                found += 1

        self.stdout.write(self.style.SUCCESS('{} found'.format(found)))
