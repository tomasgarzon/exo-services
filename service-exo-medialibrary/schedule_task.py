import schedule
import time
import os
import django

from django.core.management import call_command


def vimeo_resources():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
    django.setup()
    call_command('import_vimeo_resources')


schedule.every().day.at('22:55').do(vimeo_resources)

while True:
    schedule.run_pending()
    time.sleep(60)
