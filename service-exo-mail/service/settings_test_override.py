import sys
from celery import current_app


TEST_MODE = sys.argv[1:2] == ['test']

if TEST_MODE:
    FORCE_SCRIPT_NAME = ''
    current_app.conf.task_always_eager = True
    current_app.conf.task_eager_propagates = True
    METRIC_URL = ''
