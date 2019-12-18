# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'health_check',
    'auth_uuid.apps.AuthConfig',
    'rest_framework',
    'drf_yasg',
    'corsheaders',
    'django_celery_results',
    'populate',
    'exo_changelog',
    'payments',
    'utils',
    'dj_anonymizer',
    'import_export',
]
