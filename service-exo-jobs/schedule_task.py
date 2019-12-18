import schedule
import time
import os
import django

from django.core.management import call_command


def update_status():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
    django.setup()
    call_command('update_job_status')


schedule.every().day.at('01:00').do(update_status)

while True:
    schedule.run_pending()
    time.sleep(60)
