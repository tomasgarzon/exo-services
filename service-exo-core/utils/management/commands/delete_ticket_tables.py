from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):

    def handle(self, *args, **options):

        try:

            # LEGACY
            with connections['default'].cursor() as cursor:
                tables_drop = [
                    'ticket_applicant_keywords',
                    'ticket_applicant_languages',
                    'ticket_applicantdialogitem_slots',
                    'ticket_applicantdialogitem',
                    'ticket_applicantslot',
                    'ticket_applicantstatus',
                    'ticket_linkapplicant',

                    'ticket_projectticketsettings',
                    'ticket_teamticketsettings',
                    'ticket_teamticketstatus',

                    'ticket_ticket_keywords',
                    'ticket_ticket_languages',
                    'ticket_ticketcancelationdetail',
                    'ticket_ticketkeyword',
                    'ticket_ticketsession',
                    'ticket_ticketstatus',
                    'ticket_collaboratorprojectrequest',

                    'ticket_applicant',
                    'ticket_ticket',
                ]

                for table in tables_drop:
                    print('Drop table: {}'.format(table))
                    cursor.execute('DROP table if exists {} CASCADE'.format(table))

            print('Finished!')

        except Exception as exc:
            print(exc)
