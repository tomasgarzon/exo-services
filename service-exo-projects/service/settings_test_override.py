from celery import current_app

FORCE_SCRIPT_NAME = '/'
current_app.conf.task_always_eager = True
current_app.conf.task_eager_propagates = True
METRIC_URL = ''
POPULATOR_MODE = True
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
