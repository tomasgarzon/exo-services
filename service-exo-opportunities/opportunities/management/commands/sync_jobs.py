from django.core.management import BaseCommand

from ...models import ApplicantSow


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('Creating jobs ...')

        for sow in ApplicantSow.objects.all():
            sow.save()

        self.stdout.write('Jobs created')
