import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from datetime import datetime

from core.management.commands.progress_bar import ProgressBar

from consultant.hubspot.contact import Contact, COMMUNITY_LIFE_CYCLE_LEAD, HubSpotException


class Command(BaseCommand):

    help = ('Update Community Life-cycle at HubSpot')
    missing_args_message = 'You must provide the file path with user emails.'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', nargs='+', type=str)

    def handle(self, *args, **options):
        file_path = options.get('file')[0]

        log = open('{}.log'.format(__file__.split('.py')[0]), 'a')
        log.write('\nExecution date {}\n\n'.format(datetime.now().date()))

        self.stdout.write(self.style.WARNING(
            'This script will update Community Life-cycle at HubSpot \n',
        ))
        self.stdout.write(self.style.NOTICE('Attention!!'))
        self.stdout.write(self.style.NOTICE(
            'You are going to generate PUBLIC changes',
        ))

        proceed = input('Do you want to proceed? (Y/[N]): ')
        if proceed.lower() == 'y':
            usr_not_exist = 0
            usr_no_consultant = 0
            usr_updated = 0
            bar = ProgressBar(
                title='Updating users to HubSpot',
                total=sum(1 for _ in open(file_path, 'r'))
            )

            with open(file_path, 'r') as csv_file:
                reader = csv.reader(csv_file, delimiter=',')
                for row in reader:
                    bar.step(message=row[0])

                    try:
                        usr = get_user_model().objects.get(email=row[0])
                    except get_user_model().DoesNotExist:
                        log.write('    Contact {} NOT EXIST at Platform \n'.format(row[0]))
                        usr = None
                        usr_not_exist += 1
                        continue

                    if usr and not hasattr(usr, 'consultant'):
                        log.write('    Contact {} is not Consultant \n'.format(usr.email))
                        usr = None
                        usr_no_consultant += 1
                        continue

                    if usr and hasattr(usr, 'consultant') and usr.consultant.status != 'A':
                        usr_updated += 1
                        hub_spot_contact = Contact.get_contact(email=usr.email)
                        try:
                            hub_spot_contact.update_property(
                                'community_life_cycle',
                                COMMUNITY_LIFE_CYCLE_LEAD
                            )
                            log.write('    Contact updated {} with {} \n'.format(
                                usr.email,
                                hub_spot_contact.get_hubspot_property('community_life_cycle'))
                            )
                            usr_updated += 1
                        except HubSpotException:
                            log.write('    ERROR: Cannot set Property {} with value {} to {} \n'.format(
                                'community_life_cycle',
                                COMMUNITY_LIFE_CYCLE_LEAD,
                                usr.email)
                            )

            log.write('\n User not Exists: {} \n'.format(usr_not_exist))
            log.write('\n User Pending: {} \n'.format(usr_updated))
            log.write('\n User no Consultant: {} \n'.format(usr_no_consultant))
            log.write('\nDone!!\n\n')

        else:
            self.stdout.write(self.style.WARNING('Aborted!'))
            log.write('\nAborted!\n')

        log.close()
