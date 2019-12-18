from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Creating agreements ...'))

        call_command('loaddata', 'agreements')

        self.stdout.write(self.style.SUCCESS('Agreements created'))
