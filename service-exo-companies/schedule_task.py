import schedule
import time
import os
import django


def do_noting():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')
    django.setup()


schedule.every().day.at('01:00').do(do_noting)

while True:
    schedule.run_pending()
    time.sleep(60)
