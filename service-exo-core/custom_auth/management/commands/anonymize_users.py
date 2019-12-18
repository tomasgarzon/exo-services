from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.conf import settings

from utils.faker_factory import faker


def email(obj):
    name = ''
    if not obj.get_full_name():
        name = 'anonymous'
    else:
        name = obj.get_full_name().replace(' ', '.').lower()
    return '{}.{}@example.com'.format(
        name,
        faker.pyint())


def save_user(user):
    user.short_name = faker.first_name()
    user.full_name = faker.name()
    user.email = email(user)
    user.bio_me = faker.text()
    user.short_me = faker.text()
    user.about_me = faker.text()
    user.profile_picture.name = None
    user.profile_picture_origin = settings.EXO_ACCOUNTS_PROFILE_PICTURE_CH_DEFAULT
    user.save()
    return user


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Anonymizing users'))
        i = 0
        users = get_user_model().objects.all().exclude(email__icontains='@openexo.com')
        for user in users:
            i += 1
            exception_raised = True
            while (exception_raised):
                try:
                    user = save_user(user)
                    user.emailaddress_set.exclude(is_primary=True).delete()
                    exception_raised = False
                except IntegrityError:
                    exception_raised = True
            if i % 100 == 0:
                self.stdout.write(self.style.WARNING('Users: {}'.format(i)))
        self.stdout.write(self.style.SUCCESS('Finish!!!'))
