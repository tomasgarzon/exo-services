import schedule
import time
import os
import django

from django.core.management import call_command


def project_change_status():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
    django.setup()
    call_command('update_project_status')


schedule.every().day.at('01:00').do(project_change_status)


while True:
    schedule.run_pending()
    time.sleep(60)
