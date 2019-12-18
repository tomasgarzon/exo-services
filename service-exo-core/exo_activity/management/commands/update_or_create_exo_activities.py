from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating ExO Activities ...'))

        call_command('loaddata', 'exo_activities')

        self.stdout.write(self.style.SUCCESS('ExO Activities created'))
