from django.core.management.base import BaseCommand
import gc

from mailer.models import Message


class Command(BaseCommand):
    help = 'Update search information'

    def handle(self, *args, **options):
        SIZE = 1000
        start = 0
        total = Message.objects.all().count()
        while (start < total):
            end = start + SIZE
            messages = Message.objects.all()[start:end]
            print("Batch {} - {}".format(start, end))
            print(messages.query)
            for message in messages:
                message.save()
                message = None
            start += SIZE
            messages = None
            gc.collect()

        self.stdout.write(self.style.SUCCESS('{} found'.format(total)))
