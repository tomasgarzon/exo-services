from faker import Factory as FakerFactory

from django.conf import settings


faker = FakerFactory.create(settings.FAKER_SETTINGS_LOCALE)
