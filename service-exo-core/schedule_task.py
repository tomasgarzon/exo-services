import schedule
import time
import os
import django

from django.core.management import call_command


def sync_badges():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
    django.setup()
    call_command('sync_marketplace_badges')
    call_command('sync_events_badges')
    call_command('create_badge_for_swarm')


def sync_jobs():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
    django.setup()


schedule.every().day.at('22:55').do(sync_badges)
schedule.every().day.at('01:00').do(sync_jobs)


while True:
    schedule.run_pending()
    time.sleep(60)
