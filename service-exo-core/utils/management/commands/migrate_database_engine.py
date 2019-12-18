import subprocess

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connections
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        DB_USER = settings.DATABASES['default']['USER']
        DB_HOST = settings.DATABASES['default']['HOST']
        DB_HOST_LEGACY = settings.DATABASES['legacy']['HOST']
        DB_PASS = settings.DATABASES['default']['PASSWORD']
        DB_NAME = settings.DATABASES['default']['NAME']
        BASE_DIR = '.'
        DUMP_FILE = 'legacy.dump'
        DUMP_PATH = '{}/{}'.format(BASE_DIR, DUMP_FILE)

        try:

            call_command('migrate', '--database', 'legacy')

            # LEGACY
            with connections['legacy'].cursor() as cursor:
                tables_alter = [
                    'accounts_user',
                    'project_project',
                    'partner_partner',
                ]

                tables_drop = [
                    'cities_continent',
                    'cities_country',
                    'cities_city',
                    'cities_region',
                    'cities_alternativename',
                    'cities_city_alt_names',
                    'cities_continent_alt_names',
                    'cities_country_alt_names',
                    'cities_country_neighbours',
                    'cities_district',
                    'cities_district_alt_names',
                    'cities_postalcode',
                    'cities_postalcode_alt_names',
                    'cities_region_alt_names',
                    'cities_subregion',
                    'cities_subregion_alt_names',
                    'spatial_ref_sys',
                ]

                # Drop columns
                for table in tables_alter:
                    print('Drop columns city and country for table: {}'.format(table))
                    cursor.execute('alter table {} DROP column if exists city_id'.format(table))
                    cursor.execute('alter table {} DROP column if exists country_id'.format(table))

                # Remove postgis extension
                print('Remove postgis extension')
                cursor.execute('DROP EXTENSION if exists postgis cascade')
                cursor.execute('DROP SCHEMA if exists topology cascade')
                cursor.execute('DROP SCHEMA if exists tiger cascade')
                cursor.execute('DROP SCHEMA if exists tiger_data cascade')

                # Drop tables
                for table in tables_drop:
                    print('Drop table: {}'.format(table))
                    cursor.execute('drop table if exists {} cascade'.format(table))

            # Dump
            print('Dump legacy database')
            subprocess.run([
                'pg_dump',
                '-h', DB_HOST_LEGACY,
                '-U', DB_USER,
                '-d', DB_NAME,
                '-Fc',
                '-f', DUMP_PATH,
            ], env={'PGPASSWORD': DB_PASS})

            # Restore
            print('Restore default postgresql database')
            subprocess.run([
                'pg_restore',
                '-h', DB_HOST,
                '-U', DB_USER,
                '-d', DB_NAME,
                DUMP_PATH,
            ], env={'PGPASSWORD': DB_PASS})

            print('Clean dump file')
            subprocess.run([
                'rm',
                DUMP_PATH,
            ])

            print('Finished!')

        except Exception as exc:
            print('\nFUcK')
            print('EXCEPTION ---->', exc)
