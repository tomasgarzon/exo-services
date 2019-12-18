from django.conf import settings

from faker import Factory as FakerFactory

faker = FakerFactory.create(settings.FAKER_SETTINGS_LOCALE)
