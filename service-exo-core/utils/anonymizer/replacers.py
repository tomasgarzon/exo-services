from django.conf import settings

from utils.faker_factory import faker


def url(anon, obj, field, val):
    return faker.url()


def image(anon, obj, field, val):
    return faker.image_url(
        settings.EXO_ACCOUNTS_DEFAULT_IMAGE_SIZE,
        settings.EXO_ACCOUNTS_DEFAULT_IMAGE_SIZE,
    )


def timezone(anon, obj, field, val):
    return faker.timezone()


def email(anon, obj, field, val):
    name = ''
    if not obj.get_full_name():
        name = 'anonymous'
    else:
        name = obj.get_full_name().replace(' ', '.').lower()
    return '{}.{}@example.com'.format(
        name,
        faker.pyint())
