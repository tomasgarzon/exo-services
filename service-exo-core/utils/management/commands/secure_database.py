from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from utils.faker_factory import faker


class Command(BaseCommand):
    help = 'Secure database from Production enviroment'

    def handle(self, *args, **options):
        # Fake Users emails
        for user in get_user_model().objects.all().exclude(email__icontains='@openexo.com'):
            faked_mail = faker.email()
            user.add_email_address(faked_mail, True)
            user.emailaddress_set.filter(is_primary=False)
