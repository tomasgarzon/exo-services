from django.core.management.base import BaseCommand

from achievement.models import Achievement
from achievement.signals.define import signal_update_profile_achievement

from ...models import Consultant


class Command(BaseCommand):
    help = 'Create coins for consultant'

    def coin_allocation(self, consultant, coins):
        if not consultant.user.achievements.exists():
            Achievement.objects.create_reward_for_consultant(
                consultant,
                coins)
        signal_update_profile_achievement.send(
            sender=consultant.__class__,
            consultant=consultant)

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('data', nargs='+', type=str)

    def handle(self, *args, **options):
        filename = options.get('data')[0]
        self.stdout.write(self.style.WARNING(
            'This script will allocate coins for consultant \n'))
        self.stdout.write(self.style.NOTICE('Attention!!'))
        self.stdout.write(self.style.NOTICE(
            'You are going to generate PUBLIC changes'))
        log = open('{}.log'.format(__file__.split('.py')[0]), 'a')
        proceed = input('Do you want to proceed? (Y/[N])')

        if proceed.lower() == 'y':
            with open(filename, 'r') as f:
                coins = 0
                for linea in f.readlines():
                    linea = linea.replace('\n', '')
                    try:
                        coins = int(linea.replace(' ', ''))
                        continue
                    except ValueError:
                        pass
                    consultant = Consultant.all_objects.filter(
                        user__full_name__iexact=linea)
                    if consultant.count() == 0:
                        self.stdout.write(
                            '%s does not exist' % (
                                self.style.ERROR('{} '.format(linea)))
                        )
                    else:
                        consultant = consultant.first()
                        self.coin_allocation(consultant, coins)
                        log.write(
                            '\nConsultant: {} -- {} '.format(
                                consultant, coins))
                        self.stdout.write(
                            '%s -- %s' % (
                                self.style.WARNING(
                                    'Consultant: {} '.format(consultant)),
                                self.style.SUCCESS('{}'.format(coins))))

            self.stdout.write(self.style.SUCCESS('\nDone!!\n'))
            log.write('\nDone!!\n')

        else:
            self.stdout.write(self.style.WARNING('Aborted!'))
            log.write('\nAborted!\n')

        log.close()
