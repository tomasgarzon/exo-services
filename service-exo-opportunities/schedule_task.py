import schedule
import time
import os
import django

from django.core.management import call_command


def opportunity_change_status():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
    django.setup()
    call_command('opportunity_deadline')
    call_command('opportunity_feedback')
    call_command('opportunity_send_summary')


def opportunity_do_report():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
    django.setup()
    call_command('opportunity_report_finance')


schedule.every().day.at('01:00').do(opportunity_change_status)
schedule.every().day.at('23:50').do(opportunity_do_report)

while True:
    schedule.run_pending()
    time.sleep(60)
