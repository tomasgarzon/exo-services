from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from datetime import datetime


class Command(BaseCommand):

    def fake_migrations(self):
        with connection.cursor() as cursor:
            now = datetime.now()
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('exo_accounts', '0001_squashed_0049_auto_20180118_1039', '{}');
                """.format(now))
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('exo_accounts', '0002_user_country', '{}');
                """.format(now))
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('exo_accounts', '0003_auto_20180328_0509', '{}');
                """.format(now))

    def handle(self, *args, **options):

        self.stdout.write(self.style.WARNING(
            'This script will migrate Tool Accounts to the new ExO Accounts app\n',
        ))
        self.stdout.write(self.style.NOTICE('Attention!!'))
        self.stdout.write(self.style.NOTICE(
            'Cancel if you are not sure about the changes',
        ))
        log = open('{}.log'.format(__file__.split('.py')[0]), 'a')
        proceed = input('Do you want to proceed? (Y/[N])')

        if proceed.lower() == 'y':
            self.fake_migrations()
            log.write('\nFake migrations .... OK\n')
            self.stdout.write(self.style.SUCCESS('\nFake migrations .... OK\n'))
            call_command('showmigrations', 'exo_accounts', verbosity=0, interactive=False, stdout=log)

            call_command('migrate', 'exo_accounts', verbosity=0, interactive=False, stdout=log)
            self.stdout.write(self.style.SUCCESS('\nApplied new migrations .... OK\n'))

            call_command('showmigrations', 'exo_accounts', verbosity=0, interactive=False, stdout=log)

            self.stdout.write(self.style.SUCCESS('\nDone!!\n'))
            log.write('\nDone!!\n')

        else:
            self.stdout.write(self.style.WARNING('Aborted!'))
            log.write('\nAborted!\n')

        log.close()
