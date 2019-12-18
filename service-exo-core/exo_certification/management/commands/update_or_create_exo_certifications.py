from django.core.management import BaseCommand, call_command


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Creating ExO Certifications ...'))

        call_command('loaddata', 'exo_certifications')

        self.stdout.write(self.style.SUCCESS('ExO Cetifications created'))
