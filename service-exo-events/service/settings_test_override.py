from celery import current_app

POPULATOR_MODE = True
ACCREDIBLE_ENABLED = True
ACCREDIBLE_SANDBOX = True
ACCREDIBLE_API_KEY = None
ACCREDIBLE_SERVER_URL = None
FORCE_SCRIPT_NAME = ''
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
current_app.conf.task_always_eager = True
current_app.conf.task_eager_propagates = True
METRIC_URL = ''
