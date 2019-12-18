from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):

    def handle(self, *args, **options):

        try:

            # LEGACY
            with connections['default'].cursor() as cursor:
                tables_drop = [
                    'consultant_role_exorole',
                ]

                tables_alter = [
                    'relation_consultantrole',
                    'relation_consultantprojectrole',
                    'relation_userprojectrole',
                ]

                for table in tables_alter:
                    print('Drop column role for table: {}'.format(table))
                    cursor.execute('alter table {} DROP column if exists role_id'.format(table))
                    cursor.execute('alter table {} DROP column if exists role_id'.format(table))

                for table in tables_drop:
                    print('Drop table: {}'.format(table))
                    cursor.execute('DROP table if exists {}'.format(table))

            print('Finished!')

        except Exception as exc:
            print(exc)
