from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Creating config params ...'))

        call_command('loaddata', 'config_attributes.json')

        self.stdout.write(self.style.SUCCESS('Config params created'))
