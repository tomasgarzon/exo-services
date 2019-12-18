import json

from django.core.management.base import BaseCommand

from exo_messages.models import Message


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('filepath', nargs='+', type=str)

    def handle(self, *args, **options):
        messages_created = 0
        total_messages = []
        filepath = options.get('filepath')[0]
        self.stdout.write(self.style.WARNING(
            'This script will migrate old InternalMessage from a json file\n',
        ))
        self.stdout.write(self.style.NOTICE('Attention!!'))
        self.stdout.write(self.style.NOTICE(
            'Cancel if you are not sure about the changes',
        ))
        log = open('{}.log'.format(__file__.split('.py')[0]), 'a')
        proceed = input('Do you want to proceed? (Y/[N])')

        if proceed.lower() == 'y':
            try:
                json_data = open(filepath, 'rb')
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR('\n Error reading file {}\n'.format(filepath)))
                return

            messages = json.loads(json_data.readline().decode('utf-8'))
            for message_item in messages:
                exo_message = message_item.get('fields')
                message, created = Message.objects.get_or_create(
                    user_id=exo_message.get('user'),
                    can_be_closed=exo_message.get('can_be_closed'),
                    read_when_login=exo_message.get('read_when_login'),
                    description=exo_message.get('description'),
                    code=exo_message.get('code'),
                    level=exo_message.get('level'),
                    variables=exo_message.get('variables'),
                    read_at=exo_message.get('read_at'),
                    deleted=exo_message.get('deleted'),
                )
                if created:
                    total_messages.append(message.user.email)
                    messages_created += 1

                    log.write('\nCreated - {} # {}'.format(
                        message.user.email,
                        message.get_code_display()))
                    self.stdout.write(self.style.SUCCESS(
                        'Created - {} # {}'.format(
                            message.user.email,
                            message.get_code_display())))
                else:
                    log.write('\nSkipped {} # {}'.format(
                        message.user.email,
                        message.get_code_display()))
                    self.stdout.write(self.style.WARNING(
                        'Skipped - {} # {}'.format(
                            message.user.email,
                            message.get_code_display())))

            log.write('\nTotal NEW Messages created, {}'.format(messages_created))
            self.stdout.write(self.style.WARNING(
                '\nTotal NEW Messages created, {}'.format(messages_created)))

            log.write('\nDone!!\n')
            self.stdout.write(self.style.SUCCESS('\nDone!!\n'))

        else:
            self.stdout.write(self.style.WARNING('Aborted!'))
            log.write('\nAborted!\n\n')

        log.close()
