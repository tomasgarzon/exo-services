import csv

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management.base import BaseCommand

from datetime import datetime

from .progress_bar import ProgressBar

from ...models import Event


class Command(BaseCommand):

    help = ('Load Events from csv')
    missing_args_message = 'You must provide the file path with user events and participants.'

    def add_arguments(self, parser):
        parser.add_argument('-e', '--events', nargs='+', type=str)

    def get_category_from_name(self, category_name):
        def filter_category(category):
            return category[0] if category[1].lower().strip() == category_name.lower().strip() else None

        return list(filter(filter_category, settings.EVENT_TYPE_CHOICES))[0]

    def create_events(self, file_path, log):
        roles_by_name = {_[1].lower(): _[0] for _ in settings.EVENT_ROLE_CHOICES}
        user_not_exists = 0
        events_created = 0
        events_not_created = []
        total_events = sum(1 for _ in open(file_path, 'r') if _[0] != '#')
        bar = ProgressBar(
            title='Creating new Events',
            total=sum(1 for _ in open(file_path, 'r'))
        )

        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter='#')
            current_event = None
            for row in reader:
                if row[2]:
                    message = 'Creating event {}'.format(row[2])
                else:
                    message = 'Adding {} to {}'.format(row[8], current_event)
                bar.step(message=message)

                if row[7]:
                    user, user_data = get_user_model().objects.retrieve_remote_user_by_uuid(
                        uuid=row[7],
                        retrieve_response=True,
                    )

                    if user and not user.is_anonymous:
                        if row[0] != '':
                            event_data = {
                                'user_from': user,
                                'title': row[2],
                                'start': datetime.strptime(row[0], '%d/%m/%Y'),
                                'end': datetime.strptime(row[0], '%d/%m/%Y'),
                                'category': self.get_category_from_name(row[1].lower().strip()),
                                'location': row[3],
                                'languages': [_.strip() for _ in row[4].split(',')],
                                'show_price': row[5].lower() == 'yes',
                                'url_image': row[9] or None,
                                'url': row[10],
                                'participants': [{'uuid': user.uuid, 'role': roles_by_name.get(row[8].lower())}]
                            }
                            current_event = Event.objects.create_event(**event_data)
                            current_event.status = (user, settings.EVENT_CH_STATUS_PUBLIC)
                            events_created += 1

                        elif current_event:
                            participant_data = {
                                'role': roles_by_name.get(row[8].lower()),
                                'uuid': user.uuid.__str__(),
                            }
                            current_event.add_participant(**participant_data)
                            events_not_created.append('{} - {}'.format(row[1], row[2]))
                    else:
                        log.write('User with uuid {} does not exsits \n'.format(row[7]))
                        user_not_exists += 1
                        continue

        self.stdout.write('Events created: {} / {} \n'.format(events_created, total_events))

        log.write('\nEvents created: {} / {} \n'.format(events_created, total_events))
        log.write('Events not created:\n')
        for _ in events_not_created:
            log.write('{}\n'.format(_))

        log.write('\nUser not Exists: {} \n'.format(user_not_exists))
        log.write('\nDone!!\n\n')

    def handle(self, *args, **options):
        events_path = options.get('events')[0]

        log = open('{}.log'.format(__file__.split('.py')[0]), 'a')
        log.write('\nExecution date {}\n\n'.format(datetime.now().date()))

        self.stdout.write(self.style.WARNING('This script will create new public Events for OpenExO Website\n'))  # noqa
        self.stdout.write(self.style.NOTICE('Attention!!\nYou are going to generate PUBLIC changes'))

        proceed = input('Do you want to proceed? (Y/[N]): ')
        if proceed.lower() == 'y':
            self.create_events(events_path, log=log)
            self.stdout.write(self.style.SUCCESS('Done!!'))
        else:
            self.stdout.write(self.style.WARNING('Aborted!'))
            log.write('\nAborted!\n')

        log.close()
