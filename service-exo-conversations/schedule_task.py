import schedule
import time
import os
import django

from django.core.management import call_command


def recap_daily():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
    django.setup()
    call_command('recap_unread_summary', '--period', 'D')


def recap_weekly():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
    django.setup()
    call_command('recap_unread_summary', '--period', 'W')


schedule.every().day.at('23:00').do(recap_daily)
schedule.every().sunday.at('23:15').do(recap_weekly)

while True:
    schedule.run_pending()
    time.sleep(60)
