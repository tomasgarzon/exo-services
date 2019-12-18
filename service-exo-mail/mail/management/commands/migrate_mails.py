from django.core.management.base import BaseCommand


def get_val_from_headers(headers, param):
    for key, val in headers:
        if key == param:
            return val


class Command(BaseCommand):
    help = 'Migrate mails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pk',
            type=int,
            help='Starting id to migrate (it won`t be included)',
        )

    def handle(self, *args, **options):
        pass
