from django.core.management.base import BaseCommand

from ...models import UserSubscription


class Command(BaseCommand):
    help = (
        'Clear users connected'
    )

    def handle(self, *args, **options):
        self.stdout.write('\n Removing users connected from DB..\n\n')
        UserSubscription.objects.all().delete()
        self.stdout.write('\n Finish!! \n\n')
