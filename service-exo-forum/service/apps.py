# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    # 'debug_toolbar',
    'django_extensions',
    'health_check',
    'auth_uuid.apps.AuthConfig',
    'rest_framework',
    'corsheaders',
    'django_celery_results',
    'timezone_field',
    'exo_changelog',
    'exo_role',
    'utils',
    'populate',
    'keywords',
    'forum',
    'ratings',
    'exo_mentions',
    'dj_anonymizer',
]
