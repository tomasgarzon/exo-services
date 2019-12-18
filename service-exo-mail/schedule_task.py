import schedule
import time
import os
import django

from django.core.management import call_command


def job_purgue_mail_log():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
    django.setup()
    call_command('purge_mail_log', '7')


schedule.every().sunday.do(job_purgue_mail_log)

while True:
    schedule.run_pending()
    time.sleep(60)
