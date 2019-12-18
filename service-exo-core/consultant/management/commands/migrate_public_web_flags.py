from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import Consultant


class Command(BaseCommand):

    def handle(self, *args, **options):

        self.stdout.write(self.style.WARNING(
            'This script will update Consultants at ExOWorks website \n',
        ))
        self.stdout.write(self.style.NOTICE('Attention!!'))
        self.stdout.write(self.style.NOTICE(
            'You are going to generate PUBLIC changes',
        ))
        log = open('{}.log'.format(__file__.split('.py')[0]), 'a')
        proceed = input('Do you want to proceed? (Y/[N])')

        if proceed.lower() == 'y':
            for consultant in Consultant.objects.filter(web_status=settings.CONSULTANT_STATUS_CH_ACTIVE):
                consultant.showing_web = settings.CONSULTANT_EXO_WORKS_SITE
                log.write('\nConsultant: {} -- updated! '.format(consultant))
                self.stdout.write(
                    '%s ... %s' % (
                        self.style.WARNING('Consultant: {} '.format(consultant)),
                        self.style.SUCCESS('updated!'),
                    ),
                )

            self.stdout.write(self.style.SUCCESS('\nDone!!\n'))
            log.write('\nDone!!\n')

        else:
            self.stdout.write(self.style.WARNING('Aborted!'))
            log.write('\nAborted!\n')

        log.close()
